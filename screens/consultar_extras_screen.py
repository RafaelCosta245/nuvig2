import flet as ft
from .base_screen import BaseScreen

class ConsultarExtrasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "consultar_extras"

    def get_content(self) -> ft.Control:
        import datetime
        from database.database_manager import DatabaseManager

        titulo = ft.Text("Pesquisar Extras Cadastradas", size=20,
                         weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER)

        txt_pesq_policial = ft.TextButton(
            "Pesquise pela matrícula:",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            )
        )
        field_policial = ft.TextField(label="Matrícula", width=200)
        col_policial = ft.Column([txt_pesq_policial, field_policial], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        txt_pesq_data = ft.TextButton(
            "Pesquise por data:",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("pesquisa por data")
        )
        field_data = ft.TextField(label="Data", width=200)
        col_data = ft.Column([txt_pesq_data, field_data], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        txt_pesq_interticio = ft.TextButton(
            "Digite o Intertício",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("Intertício acionado")
        )

        # Busca o intertício da data atual
        hoje = datetime.date.today()
        db_manager = DatabaseManager()
        db_manager.init_database()
        interticio_nome = ""
        try:
            query = (
                "SELECT nome FROM interticios "
                "WHERE date(?) BETWEEN date(data_inicial) AND date(data_final) LIMIT 1"
            )
            result = db_manager.execute_query(query, (hoje.strftime("%Y-%m-%d"),))
            if result and len(result) > 0:
                if isinstance(result[0], dict) or hasattr(result[0], "keys"):
                    interticio_nome = result[0]["nome"]
                else:
                    interticio_nome = result[0][0]
        except Exception as e:
            interticio_nome = ""

        field_interticio = ft.TextField(label="Intertício", width=200, value=interticio_nome)
        col_interticio = ft.Column([txt_pesq_interticio, field_interticio], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        filtros_row = ft.Row([
            col_policial,
            col_data,
            col_interticio
        ], spacing=40, alignment=ft.MainAxisAlignment.CENTER)

        tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Intertício")),
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Policial")),
                ft.DataColumn(ft.Text("Turno")),
                ft.DataColumn(ft.Text("Operação")),
                ft.DataColumn(ft.Text("Início")),
                ft.DataColumn(ft.Text("Fim")),
                ft.DataColumn(ft.Text("Quant. Horas")),
            ],
            rows=[]
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
            db_manager = DatabaseManager()
            db_manager.init_database()
            matricula_val = field_policial.value.strip()
            data_val = field_data.value.strip()
            interticio_val = field_interticio.value.strip()
            policial_id = None
            policial_nome = ""
            filtros = []
            params = []

            if matricula_val:
                query_policial = "SELECT id, nome FROM policiais WHERE matricula = ?"
                result_policial = db_manager.execute_query(query_policial, (matricula_val,))
                if result_policial:
                    policial_id = result_policial[0]["id"] if hasattr(result_policial[0], "keys") else result_policial[0][0]
                    policial_nome = result_policial[0]["nome"] if hasattr(result_policial[0], "keys") else ""
                    filtros.append("policial_id = ?")
                    params.append(policial_id)

            data_id = None
            if data_val and len(data_val) == 10:
                partes = data_val.split("/")
                if len(partes) == 3:
                    data_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    query_data = "SELECT id FROM calendario WHERE data = ?"
                    result_data = db_manager.execute_query(query_data, (data_sql,))
                    if result_data:
                        data_id = result_data[0]["id"] if hasattr(result_data[0], "keys") else result_data[0][0]
                        filtros.append("data_id = ?")
                        params.append(data_id)

            if interticio_val:
                filtros.append("interticio = ?")
                params.append(interticio_val)

            where_clause = " AND ".join(filtros) if filtros else "1=1"
            query_extras = f"SELECT interticio, data_id, policial_id, turno, operacao, inicio, fim, horas FROM extras WHERE {where_clause}"
            result_extras = db_manager.execute_query(query_extras, tuple(params))

            tabela.rows.clear()
            for row in result_extras:
                policial_nome_row = policial_nome
                if not policial_nome_row:
                    query_nome = "SELECT nome FROM policiais WHERE id = ?"
                    res_nome = db_manager.execute_query(query_nome, (row["policial_id"],)) if hasattr(row, "keys") else db_manager.execute_query(query_nome, (row[2],))
                    policial_nome_row = res_nome[0]["nome"] if res_nome and hasattr(res_nome[0], "keys") else (res_nome[0][0] if res_nome else "")
                query_data_val = "SELECT data FROM calendario WHERE id = ?"
                res_data_val = db_manager.execute_query(query_data_val, (row["data_id"],)) if hasattr(row, "keys") else db_manager.execute_query(query_data_val, (row[1],))
                data_val_row = res_data_val[0]["data"] if res_data_val and hasattr(res_data_val[0], "keys") else (res_data_val[0][0] if res_data_val else "")
                tabela.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(row["interticio"] if hasattr(row, "keys") else row[0])),
                    ft.DataCell(ft.Text(data_val_row)),
                    ft.DataCell(ft.Text(policial_nome_row)),
                    ft.DataCell(ft.Text(row["turno"] if hasattr(row, "keys") else row[3])),
                    ft.DataCell(ft.Text(row["operacao"] if hasattr(row, "keys") else row[4])),
                    ft.DataCell(ft.Text(row["inicio"] if hasattr(row, "keys") else row[5])),
                    ft.DataCell(ft.Text(row["fim"] if hasattr(row, "keys") else row[6])),
                    ft.DataCell(ft.Text(row["horas"] if hasattr(row, "keys") else row[7])),
                ]))
            tabela.update()
            # Fecha explicitamente a conexão para evitar erro de thread
            if hasattr(db_manager, "close_connection"):
                db_manager.close_connection()

        field_policial.on_change = atualizar_tabela
        field_data.on_change = atualizar_tabela
        field_interticio.on_change = atualizar_tabela

        btn_apagar = ft.TextButton(
            "Apagar",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("Apagar acionado")
        )
        btn_editar = ft.TextButton(
            "Editar",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("Editar acionado")
        )
        btn_gravar = ft.TextButton(
            "Gravar",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("Gravar acionado")
        )
        row_botoes = ft.Row([
            btn_apagar,
            btn_editar,
            btn_gravar
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
