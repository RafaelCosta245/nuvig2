import flet as ft
import datetime
from .base_screen import BaseScreen


class CadastrarTacScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "cadastrar_tac"

	def get_content(self) -> ft.Control:
		# Função para buscar policial pela matrícula
		def buscar_policial(e):
			valor = matricula.value.strip()
			if valor:
				policial_info = self.app.db.get_policial_by_matricula(valor)
				if policial_info:
					policial.value = policial_info.get("qra", "")
					nome.value = policial_info.get("nome", "")
					escala = policial_info.get("escala", "")
					equipe.value = escala[0] if escala else ""
				else:
					policial.value = ""
					nome.value = ""
					equipe.value = ""
			else:
				policial.value = ""
				nome.value = ""
				equipe.value = ""
			e.control.page.update()

		# Buscar por QRA ou Nome (EXATO) e preencher matrícula, nome e equipe
		def buscar_policial_por_qra_ou_nome(e):
			termo = policial.value.strip()
			if not termo:
				e.control.page.update()
				return
			try:
				query = """
					SELECT id, nome, qra, matricula, escala
					FROM policiais
					WHERE unidade = 'NUVIG'
					  AND (UPPER(qra) = UPPER(?) OR UPPER(nome) = UPPER(?))
					LIMIT 1
				"""
				rows = self.app.db.execute_query(query, (termo, termo))
				if rows:
					row = rows[0]
					matricula.value = (row["matricula"] if "matricula" in row.keys() else matricula.value) or matricula.value
					policial.value = (row["qra"] if "qra" in row.keys() else policial.value) or policial.value
					nome.value = (row["nome"] if "nome" in row.keys() else nome.value) or nome.value
					escala = row["escala"] if "escala" in row.keys() else ""
					equipe.value = escala[0] if escala else equipe.value
			except Exception as err:
				print(f"[CadastrarTac] Erro ao buscar por QRA/Nome: {err}")
			e.control.page.update()


		# Campos do formulário
		matricula = ft.TextField(
			label="Matrícula",
			bgcolor=ft.Colors.WHITE,
			width=200,
			input_filter=ft.NumbersOnlyInputFilter(),
			on_change=buscar_policial
		)
		policial = ft.TextField(
			label="QRA",
			bgcolor=ft.Colors.WHITE,
			width=200,
			read_only=False,
		)
		nome = ft.TextField(
			label="Nome",
			bgcolor=ft.Colors.WHITE,
			width=200,
			read_only=True,
			disabled=True,
		)
		equipe = ft.TextField(
			label="Equipe",
			bgcolor=ft.Colors.WHITE,
			width=200,
			read_only=True,
			disabled=True,
		)
		data1 = ft.TextField(label="Data do TAC",
							 width=200,
							 hint_text="dd/mm/aaaa",
							 bgcolor=ft.Colors.WHITE)
		processo = ft.TextField(
			label="Processo",
			bgcolor=ft.Colors.WHITE,
			width=(equipe.width*2 + 32),
		)


		# Função para aplicar máscara de data
		def mascara_data1(e):
			valor = ''.join([c for c in data1.value if c.isdigit()])
			novo_valor = ''
			if len(valor) > 0:
				novo_valor += valor[:2]
			if len(valor) > 2:
				novo_valor += '/' + valor[2:4]
			if len(valor) > 4:
				novo_valor += '/' + valor[4:8]
			data1.value = novo_valor
			e.control.page.update()

		data1.on_change = mascara_data1
		policial.on_change = buscar_policial_por_qra_ou_nome

		# DatePicker para Data do TAC
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
			text="Data do TAC",
			icon=ft.Icons.CALENDAR_MONTH,
			bgcolor=ft.Colors.WHITE,
			color=ft.Colors.BLACK,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
			),
			width=matricula.width,
			height=matricula.height,
			on_click=open_date_picker1
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
				processo
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
		], spacing=24, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

		# Função para mostrar AlertDialog de sucesso/erro
		def mostrar_resultado_gravacao(page, sucesso, mensagem):
			def fechar_dialogo(e):
				page.close(dialogo_resultado)

			cor_titulo = ft.Colors.GREEN if sucesso else ft.Colors.RED
			titulo = "Sucesso!" if sucesso else "Erro!"

			dialogo_resultado = ft.AlertDialog(
				modal=True,
				title=ft.Text(titulo, color=cor_titulo, weight=ft.FontWeight.BOLD),
				content=ft.Text(mensagem, size=14),
				actions=[
					ft.TextButton("OK", on_click=fechar_dialogo)
				],
				actions_alignment=ft.MainAxisAlignment.END,
			)
			page.open(dialogo_resultado)

		# Função para gravar TAC
		def gravar_tac(e):
			# Validar campos obrigatórios
			if not matricula.value.strip():
				mostrar_resultado_gravacao(e.control.page, False, "Matrícula é obrigatória!")
				return

			if not data1.value.strip():
				mostrar_resultado_gravacao(e.control.page, False, "Data do TAC é obrigatória!")
				return

			if not processo.value.strip():
				mostrar_resultado_gravacao(e.control.page, False, "Processo é obrigatório!")
				return

			try:
				# Buscar o ID do policial pela matrícula
				query_policial = "SELECT id FROM policiais WHERE matricula = ?"
				result_policial = self.app.db.execute_query(query_policial, (matricula.value.strip(),))

				if not result_policial:
					mostrar_resultado_gravacao(e.control.page, False, "Policial não encontrado!")
					return

				policial_id = result_policial[0]["id"] if hasattr(result_policial[0], "keys") else result_policial[0][0]

				# Converter data para formato SQL (aaaa-mm-dd)
				data_tac = datetime.datetime.strptime(data1.value, "%d/%m/%Y").strftime("%Y-%m-%d")

				# Inserir na tabela tacs
				query_insert = """
					INSERT INTO tacs (policial_id, data, processo)
					VALUES (?, ?, ?)
				"""

				success = self.app.db.execute_command(
					query_insert,
					(policial_id, data_tac, processo.value.strip())
				)

				if success:
					mostrar_resultado_gravacao(
						e.control.page,
						True,
						f"TAC gravado com sucesso!\n\n"
						f"Policial: {nome.value}\n"
						f"Data: {data1.value}\n"
						f"Processo: {processo.value}"
					)
					limpar_formulario(e)
				else:
					mostrar_resultado_gravacao(e.control.page, False, "Erro ao gravar o TAC!")

			except ValueError as ve:
				mostrar_resultado_gravacao(e.control.page, False, f"Formato de data inválido: {str(ve)}")
			except Exception as ex:
				mostrar_resultado_gravacao(e.control.page, False, f"Erro inesperado: {str(ex)}")

		# Função para limpar o formulário
		def limpar_formulario(e):
			matricula.value = ""
			policial.value = ""
			nome.value = ""
			equipe.value = ""
			data1.value = ""
			processo.value = ""
			matricula.update()
			policial.update()
			nome.update()
			equipe.update()
			data1.update()
			processo.update()

		# Botões
		btn_gravar = ft.ElevatedButton(
			text="Gravar",
			style=ft.ButtonStyle(
				color=ft.Colors.BLACK,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.GREEN)),
			icon=ft.Icons.SAVE,
			color=ft.Colors.GREEN,
			width=150,
			bgcolor=ft.Colors.WHITE,
			on_click=gravar_tac
		)
		btn_limpar = ft.ElevatedButton(
			text="Limpar",
			width=btn_gravar.width,
			style=ft.ButtonStyle(
				color=ft.Colors.BLACK,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.RED)),
			icon=ft.Icons.DELETE,
			bgcolor=ft.Colors.WHITE,
			color=ft.Colors.RED,
			on_click=limpar_formulario
		)
		btn_row = ft.Row([
			btn_gravar,
			btn_limpar
		], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

		return ft.Column([
			ft.Text("Cadastrar TAC", size=28, weight=ft.FontWeight.BOLD,
					color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
			ft.Container(height=20),
			form_grid,
			ft.Container(height=30),
			btn_row
		], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
