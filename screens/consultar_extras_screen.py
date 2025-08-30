import flet as ft
from .base_screen import BaseScreen

class ConsultarExtrasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "consultar_extras"

    def get_content(self) -> ft.Control:
        # Título
        titulo = ft.Text("Pesquisar Extras Cadastradas", size=20,
                         weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER)

        # Filtros de pesquisa
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
        import datetime
        from database.database_manager import DatabaseManager

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
                # Se for sqlite3.Row, acessar por nome
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

        # Container para tabela de resultados
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
        tabela_container = ft.Container(
            content=tabela,
            #bgcolor=ft.Colors.GREEN,
            padding=0,
            expand=True,
            width=1200 * 1.2  # 20% maior que 1200px (ajuste conforme necessário)
        )

        # Row de botões de ação
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
