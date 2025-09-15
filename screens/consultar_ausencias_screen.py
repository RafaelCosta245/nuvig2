import flet as ft
from .base_screen import BaseScreen


class ConsultarAusenciasScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "consultar_ausencias"

	def get_content(self) -> ft.Control:
		import datetime

		# Título e filtro (apenas matrícula)
		titulo = ft.Text(
			"Consultar Ausências por Matrícula",
			size=20,
			weight=ft.FontWeight.BOLD,
			color=ft.Colors.BLACK,
			text_align=ft.TextAlign.CENTER,
		)
		field_policial = ft.TextField(label="Matrícula", width=200)
		filtros_row = ft.Row([field_policial], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

		# Tabela resultado
		tabela = ft.DataTable(
			columns=[
				ft.DataColumn(ft.Text("Nome")),
				ft.DataColumn(ft.Text("QRA")),
				ft.DataColumn(ft.Text("Licença")),
				ft.DataColumn(ft.Text("Início")),
				ft.DataColumn(ft.Text("Fim")),
				ft.DataColumn(ft.Text("Dias")),
				ft.DataColumn(ft.Text("Retorno")),
			],
			rows=[],
			show_checkbox_column=False,
		)
		tabela_container = ft.Container(
			content=ft.ListView(controls=[tabela], expand=True, padding=0, spacing=0),
			padding=0,
			expand=True,
			width=1000,
		)

		def _format_date(sql_date: str) -> str:
			try:
				if not sql_date:
					return ""
				y, m, d = sql_date.split("-")
				return f"{d}/{m}/{y}"
			except Exception:
				return sql_date or ""

		def atualizar_tabela(_=None):
			matricula = field_policial.value.strip()
			tabela.rows.clear()
			if not matricula:
				tabela.update()
				return

			# Buscar policial
			db = self.app.db
			res_pol = db.execute_query("SELECT id, nome, qra FROM policiais WHERE matricula = ?", (matricula,))
			if not res_pol:
				tabela.update()
				return
			pol = res_pol[0]
			pid = pol["id"] if hasattr(pol, "keys") else pol[0]
			nome = pol["nome"] if hasattr(pol, "keys") else pol[1]
			qra = pol["qra"] if hasattr(pol, "keys") else pol[2]

			# Buscar licenças para o policial
			lics = db.execute_query(
				"SELECT licenca, inicio, fim, qty_dias FROM licencas WHERE policial_id = ? ORDER BY inicio DESC",
				(pid,),
			)

			for r in lics:
				licenca = r["licenca"] if hasattr(r, "keys") else r[0]
				inicio = r["inicio"] if hasattr(r, "keys") else r[1]
				fim = r["fim"] if hasattr(r, "keys") else r[2]
				dias = r["qty_dias"] if hasattr(r, "keys") else r[3]
				try:
					retorno = (
						datetime.datetime.strptime(fim, "%Y-%m-%d") + datetime.timedelta(days=1)
					).strftime("%d/%m/%Y")
				except Exception:
					retorno = ""
				tabela.rows.append(
					ft.DataRow(
						cells=[
							ft.DataCell(ft.Text(nome)),
							ft.DataCell(ft.Text(qra or "")),
							ft.DataCell(ft.Text(licenca or "")),
							ft.DataCell(ft.Text(_format_date(inicio))),
							ft.DataCell(ft.Text(_format_date(fim))),
							ft.DataCell(ft.Text(str(dias) if dias is not None else "")),
							ft.DataCell(ft.Text(retorno)),
						]
					)
				)

			tabela.update()

		field_policial.on_change = atualizar_tabela

		return ft.Column([
			titulo,
			ft.Container(height=10),
			filtros_row,
			ft.Container(height=16),
			tabela_container,
		], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.START, spacing=4)
