import flet as ft
from .base_screen import BaseScreen
from dialogalert import show_alert_dialog


class ConsultarTacScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "consultar_tac"

	def get_content(self) -> ft.Control:
		import datetime
		from database.database_manager import DatabaseManager

		titulo = ft.Text("Pesquisar TAC's Cadastrados", size=20,
						 weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER)

		txt_pesq_qra = ft.TextButton(
			"Pesquise pelo QRA:",
			style=ft.ButtonStyle(
				color=ft.Colors.BLACK,
				text_style=ft.TextStyle(size=12)
			)
		)
		field_qra = ft.TextField(label="QRA",
								 bgcolor=ft.Colors.WHITE,
								 width=200)
		col_qra = ft.Column([txt_pesq_qra, field_qra], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

		txt_pesq_policial = ft.TextButton(
			"Pesquise pela matrícula:",
			style=ft.ButtonStyle(
				color=ft.Colors.BLACK,
				text_style=ft.TextStyle(size=12)
			)
		)
		field_policial = ft.TextField(label="Matrícula",
									  width=200,
									  bgcolor=ft.Colors.WHITE,
									  max_length=8)
		col_policial = ft.Column([txt_pesq_policial, field_policial], spacing=8,
								 horizontal_alignment=ft.CrossAxisAlignment.CENTER)

		txt_pesq_data = ft.TextButton(
			"Pesquise por data:",
			style=ft.ButtonStyle(
				color=ft.Colors.BLACK,
				text_style=ft.TextStyle(size=12)
			)
		)
		field_data = ft.TextField(label="Data",
								  width=200,
								  bgcolor=ft.Colors.WHITE,
								  hint_text="dd/mm/aaaa")

		# Função para aplicar máscara de data
		def mascara_data(e):
			valor = ''.join([c for c in field_data.value if c.isdigit()])
			novo_valor = ''
			if len(valor) > 0:
				novo_valor += valor[:2]
			if len(valor) > 2:
				novo_valor += '/' + valor[2:4]
			if len(valor) > 4:
				novo_valor += '/' + valor[4:8]
			field_data.value = novo_valor
			e.control.page.update()

		col_data = ft.Column([txt_pesq_data, field_data], spacing=8,
							 horizontal_alignment=ft.CrossAxisAlignment.CENTER)

		filtros_row = ft.Row([
			col_qra,
			col_policial,
			col_data
		], spacing=40, alignment=ft.MainAxisAlignment.CENTER)

		# Controle para seleção única e cor de linha
		self.selected_row_index = None
		self.tabela_rows = []  # Guardar referências das linhas
		self.result_tacs = []  # Guardar os dados dos TACs para referência

		def on_row_select(e):
			row = e.control  # DataRow que disparou o evento
			idx = None
			# Descobrir índice da linha clicada
			for i, r in enumerate(self.tabela_rows):
				if r is row:
					idx = i
					break
			if idx is None:
				return
			# Não permitir toggle: só marca se não estiver marcada
			if self.selected_row_index == idx:
				return
			# Desmarca todas as linhas
			for i, r in enumerate(self.tabela_rows):
				r.selected = False
				r.color = None
			# Marca a linha clicada
			row.selected = True
			row.color = ft.Colors.GREY
			self.selected_row_index = idx
			tabela.selected_index = idx
			print(f'Linha selecionada: {idx}')
			tabela.update()

		tabela = ft.DataTable(
			columns=[
				ft.DataColumn(ft.Text("Policial")),
				ft.DataColumn(ft.Text("Matrícula")),
				ft.DataColumn(ft.Text("Data do TAC")),
				ft.DataColumn(ft.Text("Protocolo")),
			],
			rows=[],
			show_checkbox_column=False
		)
		tabela_listview = ft.ListView(
			controls=[tabela],
			spacing=0,
			padding=0,
			expand=True,
			width=1200 * 1.2
		)
		tabela_container = ft.Container(
			content=tabela_listview,
			padding=0,
			expand=True,
			width=1200 * 1.2
		)

		def atualizar_tabela(_=None):
			db_manager = self.app.db
			matricula_val = field_policial.value.strip()
			qra_val = field_qra.value.strip()
			data_val = field_data.value.strip()
			policial_id = None
			policial_nome = ""
			policial_matricula = ""
			filtros = []
			params = []

			if matricula_val:
				query_policial = "SELECT id, nome, matricula FROM policiais WHERE matricula = ?"
				result_policial = db_manager.execute_query(query_policial, (matricula_val,))
				if result_policial:
					policial_id = result_policial[0]["id"] if hasattr(result_policial[0], "keys") else result_policial[0][0]
					policial_nome = result_policial[0]["nome"] if hasattr(result_policial[0], "keys") else result_policial[0][1]
					policial_matricula = result_policial[0]["matricula"] if hasattr(result_policial[0], "keys") else result_policial[0][2]
					filtros.append("policial_id = ?")
					params.append(policial_id)

			if qra_val:
				query_policial_qra = "SELECT id, nome, matricula FROM policiais WHERE UPPER(qra) = UPPER(?)"
				result_policial_qra = db_manager.execute_query(query_policial_qra, (qra_val,))
				if result_policial_qra:
					policial_id = result_policial_qra[0]["id"] if hasattr(result_policial_qra[0], "keys") else result_policial_qra[0][0]
					policial_nome = result_policial_qra[0]["nome"] if hasattr(result_policial_qra[0], "keys") else result_policial_qra[0][1]
					policial_matricula = result_policial_qra[0]["matricula"] if hasattr(result_policial_qra[0], "keys") else result_policial_qra[0][2]
					filtros.append("policial_id = ?")
					params.append(policial_id)

			if data_val and len(data_val) == 10:
				partes = data_val.split("/")
				if len(partes) == 3:
					data_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
					filtros.append("date(data) = ?")
					params.append(data_sql)

			where_clause = " AND ".join(filtros) if filtros else "1=1"
			query_tacs = f"SELECT policial_id, data, processo FROM tacs WHERE {where_clause}"
			result_tacs = db_manager.execute_query(query_tacs, tuple(params))

			# Armazenar os resultados para referência
			self.result_tacs = result_tacs

			tabela.rows.clear()
			self.tabela_rows.clear()
			for idx, row in enumerate(result_tacs):
				policial_nome_row = policial_nome
				policial_matricula_row = policial_matricula
				if not policial_nome_row:
					query_nome = "SELECT nome, matricula FROM policiais WHERE id = ?"
					res_nome = db_manager.execute_query(query_nome, (row["policial_id"],)) if hasattr(row, "keys") else db_manager.execute_query(query_nome, (row[0],))
					if res_nome:
						policial_nome_row = res_nome[0]["nome"] if hasattr(res_nome[0], "keys") else res_nome[0][0]
						policial_matricula_row = res_nome[0]["matricula"] if hasattr(res_nome[0], "keys") else res_nome[0][1]

				# Converter datas para formato brasileiro
				def formatar_data(data_sql):
					try:
						from datetime import datetime
						data_obj = datetime.strptime(data_sql, "%Y-%m-%d")
						return data_obj.strftime("%d/%m/%Y")
					except:
						return data_sql

				data_tac = row["data"] if hasattr(row, "keys") else row[1]
				processo = row["processo"] if hasattr(row, "keys") else row[2]

				dr = ft.DataRow(
					selected=(self.selected_row_index == idx),
					on_select_changed=on_row_select,
					color=ft.Colors.GREY_200 if self.selected_row_index == idx else None,
					cells=[
						ft.DataCell(ft.Text(policial_nome_row)),
						ft.DataCell(ft.Text(policial_matricula_row)),
						ft.DataCell(ft.Text(formatar_data(data_tac))),
						ft.DataCell(ft.Text(processo)),
					]
				)
				tabela.rows.append(dr)
				self.tabela_rows.append(dr)
			tabela.update()

		field_policial.on_change = atualizar_tabela
		field_qra.on_change = atualizar_tabela

		# Função combinada para aplicar máscara e atualizar tabela
		def mascara_e_atualizar_data(e):
			mascara_data(e)
			atualizar_tabela()

		field_data.on_change = mascara_e_atualizar_data

		# Função para apagar o TAC selecionado
		def apagar_tac(e):
			if self.selected_row_index is None:
				show_alert_dialog(e.control.page, "Selecione uma linha para apagar!", success=False)
				return

			# Obter os dados do TAC selecionado
			tac_selecionado = self.result_tacs[self.selected_row_index]

			# Criar diálogo de confirmação
			def confirmar_apagar(e):
				try:
					# Construir a query de exclusão
					policial_id = tac_selecionado["policial_id"] if hasattr(tac_selecionado, "keys") else tac_selecionado[0]
					data = tac_selecionado["data"] if hasattr(tac_selecionado, "keys") else tac_selecionado[1]
					processo = tac_selecionado["processo"] if hasattr(tac_selecionado, "keys") else tac_selecionado[2]

					# Query de exclusão
					delete_query = """
						DELETE FROM tacs 
						WHERE policial_id = ? AND data = ? AND processo = ?
					"""

					# Executar a exclusão
					success = self.app.db.execute_command(delete_query, (policial_id, data, processo))

					if success:
						show_alert_dialog(e.control.page, "TAC apagado com sucesso!", success=True)
						# Limpar seleção
						self.selected_row_index = None
						# Atualizar a tabela
						atualizar_tabela()
					else:
						show_alert_dialog(e.control.page, "Erro ao apagar o TAC!", success=False)

				except Exception as ex:
					show_alert_dialog(e.control.page, f"Erro ao apagar: {str(ex)}", success=False)

				# Fechar o diálogo
				e.control.page.close(dlg_confirmacao)

			def cancelar_apagar(e):
				e.control.page.close(dlg_confirmacao)

			# Função para formatar data no diálogo
			def formatar_data(data_sql):
				try:
					from datetime import datetime
					data_obj = datetime.strptime(data_sql, "%Y-%m-%d")
					return data_obj.strftime("%d/%m/%Y")
				except:
					return data_sql

			# Criar o diálogo de confirmação
			dlg_confirmacao = ft.AlertDialog(
				modal=True,
				title=ft.Text("Confirmar Exclusão", color=ft.Colors.RED),
				content=ft.Text(
					f"Tem certeza que deseja apagar este TAC?\n\n"
					f"Data: {formatar_data(tac_selecionado['data'] if hasattr(tac_selecionado, 'keys') else tac_selecionado[1])}\n"
					f"Processo: {tac_selecionado['processo'] if hasattr(tac_selecionado, 'keys') else tac_selecionado[2]}"
				),
				actions=[
					ft.TextButton("Cancelar", on_click=cancelar_apagar),
					ft.TextButton("Apagar", on_click=confirmar_apagar, style=ft.ButtonStyle(color=ft.Colors.RED)),
				],
				actions_alignment=ft.MainAxisAlignment.END,
			)

			e.control.page.open(dlg_confirmacao)

		btn_apagar = ft.ElevatedButton(
			text="Apagar",
			width=150,
			bgcolor=ft.Colors.WHITE,
			style=ft.ButtonStyle(
				color=ft.Colors.RED,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.RED)),
			icon=ft.Icons.DELETE,
			on_click=apagar_tac
		)
		row_botoes = ft.Row([
			btn_apagar
		], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

		return ft.Column([
			titulo,
			ft.Container(height=10),
			filtros_row,
			ft.Container(height=16),
			tabela_container,
			row_botoes
		],
			horizontal_alignment=ft.CrossAxisAlignment.CENTER,
			alignment=ft.MainAxisAlignment.START,
			spacing=4)
