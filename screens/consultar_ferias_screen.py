import flet as ft
from .base_screen import BaseScreen
from dialogalert import show_alert_dialog

class ConsultarFeriasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "consultar_ferias"

    def get_content(self) -> ft.Control:
        import datetime
        from database.database_manager import DatabaseManager

        titulo = ft.Text("Pesquisar Férias Cadastradas", size=20,
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

        txt_pesq_periodo = ft.TextButton(
            "Pesquise por período aquisitivo:",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("pesquisa por período aquisitivo")
        )
        field_periodo = ft.TextField(label="Período Aquisitivo", width=200)
        col_periodo = ft.Column([txt_pesq_periodo, field_periodo], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

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

        filtros_row = ft.Row([
            col_policial,
            col_periodo,
            col_data
        ], spacing=40, alignment=ft.MainAxisAlignment.CENTER)

        # Controle para seleção única e cor de linha
        self.selected_row_index = None
        self.tabela_rows = []  # Guardar referências das linhas
        self.result_ferias = []  # Guardar os dados das férias para referência
        
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
                ft.DataColumn(ft.Text("Período Aquisitivo")),
                ft.DataColumn(ft.Text("Período 1")),
                ft.DataColumn(ft.Text("Período 2")),
                ft.DataColumn(ft.Text("Período 3")),
                ft.DataColumn(ft.Text("Total Dias")),
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
            periodo_val = field_periodo.value.strip()
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

            if periodo_val:
                filtros.append("periodo_aquisitivo = ?")
                params.append(periodo_val)

            if data_val and len(data_val) == 10:
                partes = data_val.split("/")
                if len(partes) == 3:
                    data_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    filtros.append("(date(inicio1) <= ? AND date(fim1) >= ?) OR (date(inicio2) <= ? AND date(fim2) >= ?) OR (date(inicio3) <= ? AND date(fim3) >= ?)")
                    params.extend([data_sql, data_sql, data_sql, data_sql, data_sql, data_sql])

            where_clause = " AND ".join(filtros) if filtros else "1=1"
            query_ferias = f"SELECT policial_id, periodo_aquisitivo, inicio1, fim1, inicio2, fim2, inicio3, fim3 FROM ferias WHERE {where_clause}"
            result_ferias = db_manager.execute_query(query_ferias, tuple(params))
            
            # Armazenar os resultados para referência
            self.result_ferias = result_ferias

            tabela.rows.clear()
            self.tabela_rows.clear()
            
            # Função para calcular dias entre duas datas
            def calcular_dias(data_inicio, data_fim):
                if not data_inicio or not data_fim:
                    return 0
                try:
                    from datetime import datetime
                    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
                    fim = datetime.strptime(data_fim, "%Y-%m-%d")
                    return (fim - inicio).days + 1
                except:
                    return 0
            
            # Função para formatar período
            def formatar_periodo(data_inicio, data_fim):
                if not data_inicio or not data_fim:
                    return "-"
                try:
                    from datetime import datetime
                    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
                    fim = datetime.strptime(data_fim, "%Y-%m-%d")
                    dias = (fim - inicio).days + 1
                    return f"{inicio.strftime('%d/%m')} a {fim.strftime('%d/%m')} ({dias}d)"
                except:
                    return "-"
            
            for idx, row in enumerate(result_ferias):
                policial_nome_row = policial_nome
                policial_matricula_row = policial_matricula
                if not policial_nome_row:
                    query_nome = "SELECT nome, matricula FROM policiais WHERE id = ?"
                    res_nome = db_manager.execute_query(query_nome, (row["policial_id"],)) if hasattr(row, "keys") else db_manager.execute_query(query_nome, (row[0],))
                    if res_nome:
                        policial_nome_row = res_nome[0]["nome"] if hasattr(res_nome[0], "keys") else res_nome[0][0]
                        policial_matricula_row = res_nome[0]["matricula"] if hasattr(res_nome[0], "keys") else res_nome[0][1]
                
                # Obter dados das férias
                if hasattr(row, "keys"):
                    periodo_aquisitivo = row["periodo_aquisitivo"]
                    inicio1 = row["inicio1"]
                    fim1 = row["fim1"]
                    inicio2 = row["inicio2"]
                    fim2 = row["fim2"]
                    inicio3 = row["inicio3"]
                    fim3 = row["fim3"]
                else:
                    periodo_aquisitivo = row[1]
                    inicio1 = row[2]
                    fim1 = row[3]
                    inicio2 = row[4]
                    fim2 = row[5]
                    inicio3 = row[6]
                    fim3 = row[7]
                
                # Calcular total de dias
                dias1 = calcular_dias(inicio1, fim1)
                dias2 = calcular_dias(inicio2, fim2)
                dias3 = calcular_dias(inicio3, fim3)
                total_dias = dias1 + dias2 + dias3
                
                dr = ft.DataRow(
                    selected=(self.selected_row_index == idx),
                    on_select_changed=on_row_select,
                    color=ft.Colors.GREY_200 if self.selected_row_index == idx else None,
                    cells=[
                        ft.DataCell(ft.Text(policial_nome_row)),
                        ft.DataCell(ft.Text(policial_matricula_row)),
                        ft.DataCell(ft.Text(str(periodo_aquisitivo))),
                        ft.DataCell(ft.Text(formatar_periodo(inicio1, fim1))),
                        ft.DataCell(ft.Text(formatar_periodo(inicio2, fim2))),
                        ft.DataCell(ft.Text(formatar_periodo(inicio3, fim3))),
                        ft.DataCell(ft.Text(f"{total_dias} dias")),
                    ]
                )
                tabela.rows.append(dr)
                self.tabela_rows.append(dr)
            tabela.update()

        field_policial.on_change = atualizar_tabela
        field_periodo.on_change = atualizar_tabela
        field_data.on_change = atualizar_tabela

        # Função para apagar as férias selecionadas
        def apagar_ferias(e):
            if self.selected_row_index is None:
                show_alert_dialog(e.control.page, "Selecione uma linha para apagar!", success=False)
                return
            
            # Obter os dados das férias selecionadas
            ferias_selecionada = self.result_ferias[self.selected_row_index]
            
            # Criar diálogo de confirmação
            def confirmar_apagar(e):
                try:
                    # Construir a query de exclusão
                    policial_id = ferias_selecionada["policial_id"] if hasattr(ferias_selecionada, "keys") else ferias_selecionada[0]
                    periodo_aquisitivo = ferias_selecionada["periodo_aquisitivo"] if hasattr(ferias_selecionada, "keys") else ferias_selecionada[1]
                    inicio1 = ferias_selecionada["inicio1"] if hasattr(ferias_selecionada, "keys") else ferias_selecionada[2]
                    
                    # Query de exclusão
                    delete_query = """
                        DELETE FROM ferias 
                        WHERE policial_id = ? AND periodo_aquisitivo = ? AND inicio1 = ?
                    """
                    
                    # Executar a exclusão
                    success = self.app.db.execute_command(delete_query, (policial_id, periodo_aquisitivo, inicio1))
                    
                    if success:
                        show_alert_dialog(e.control.page, "Férias apagadas com sucesso!", success=True)
                        # Limpar seleção
                        self.selected_row_index = None
                        # Atualizar a tabela
                        atualizar_tabela()
                    else:
                        show_alert_dialog(e.control.page, "Erro ao apagar as férias!", success=False)
                        
                except Exception as ex:
                    show_alert_dialog(e.control.page, f"Erro ao apagar: {str(ex)}", success=False)
                
                # Fechar o diálogo
                e.control.page.close(dlg_confirmacao)
            
            def cancelar_apagar(e):
                e.control.page.close(dlg_confirmacao)
            
            # Função para formatar período no diálogo
            def formatar_periodo_dialogo(data_inicio, data_fim):
                if not data_inicio or not data_fim:
                    return "-"
                try:
                    from datetime import datetime
                    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
                    fim = datetime.strptime(data_fim, "%Y-%m-%d")
                    return f"{inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
                except:
                    return data_inicio if data_inicio else "-"
            
            # Obter dados para o diálogo
            if hasattr(ferias_selecionada, "keys"):
                periodo = ferias_selecionada["periodo_aquisitivo"]
                inicio1 = ferias_selecionada["inicio1"]
                fim1 = ferias_selecionada["fim1"]
                inicio2 = ferias_selecionada["inicio2"]
                fim2 = ferias_selecionada["fim2"]
                inicio3 = ferias_selecionada["inicio3"]
                fim3 = ferias_selecionada["fim3"]
            else:
                periodo = ferias_selecionada[1]
                inicio1 = ferias_selecionada[2]
                fim1 = ferias_selecionada[3]
                inicio2 = ferias_selecionada[4]
                fim2 = ferias_selecionada[5]
                inicio3 = ferias_selecionada[6]
                fim3 = ferias_selecionada[7]
            
            periodos_texto = f"Período Aquisitivo: {periodo}\n"
            periodos_texto += f"Período 1: {formatar_periodo_dialogo(inicio1, fim1)}\n"
            if inicio2 and fim2:
                periodos_texto += f"Período 2: {formatar_periodo_dialogo(inicio2, fim2)}\n"
            if inicio3 and fim3:
                periodos_texto += f"Período 3: {formatar_periodo_dialogo(inicio3, fim3)}"
            
            # Criar o diálogo de confirmação
            dlg_confirmacao = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar Exclusão", color=ft.Colors.RED),
                content=ft.Text(
                    f"Tem certeza que deseja apagar estas férias?\n\n{periodos_texto}"
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=cancelar_apagar),
                    ft.TextButton("Apagar", on_click=confirmar_apagar, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            e.control.page.open(dlg_confirmacao)

        btn_apagar = ft.TextButton(
            "Apagar",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=apagar_ferias
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
