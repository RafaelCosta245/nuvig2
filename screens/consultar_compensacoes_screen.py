import flet as ft
from .base_screen import BaseScreen
from dialogalert import show_alert_dialog

class ConsultarCompensacoesScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "consultar_compensacoes"

    def get_content(self) -> ft.Control:
        import datetime
        from database.database_manager import DatabaseManager

        titulo = ft.Text("Pesquisar Compensações Cadastradas", size=20,
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

        txt_pesq_data_compensacao = ft.TextButton(
            "Pesquise por data de compensação:",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("pesquisa por data de compensação")
        )
        field_data_compensacao = ft.TextField(label="Data Compensação", width=200)
        col_data_compensacao = ft.Column([txt_pesq_data_compensacao, field_data_compensacao], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        txt_pesq_data_a_compensar = ft.TextButton(
            "Pesquise por data a compensar:",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("pesquisa por data a compensar")
        )
        field_data_a_compensar = ft.TextField(label="Data A Compensar", width=200)
        col_data_a_compensar = ft.Column([txt_pesq_data_a_compensar, field_data_a_compensar], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        filtros_row = ft.Row([
            col_policial,
            col_data_compensacao,
            col_data_a_compensar
        ], spacing=40, alignment=ft.MainAxisAlignment.CENTER)

        # Controle para seleção única e cor de linha
        self.selected_row_index = None
        self.tabela_rows = []  # Guardar referências das linhas
        self.result_compensacoes = []  # Guardar os dados das compensações para referência
        
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
                ft.DataColumn(ft.Text("Data Compensação")),
                ft.DataColumn(ft.Text("Data A Compensar")),
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
            data_compensacao_val = field_data_compensacao.value.strip()
            data_a_compensar_val = field_data_a_compensar.value.strip()
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

            if data_compensacao_val and len(data_compensacao_val) == 10:
                partes = data_compensacao_val.split("/")
                if len(partes) == 3:
                    data_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    filtros.append("date(compensacao) = ?")
                    params.append(data_sql)

            if data_a_compensar_val and len(data_a_compensar_val) == 10:
                partes = data_a_compensar_val.split("/")
                if len(partes) == 3:
                    data_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    filtros.append("date(a_compensar) = ?")
                    params.append(data_sql)

            where_clause = " AND ".join(filtros) if filtros else "1=1"
            query_compensacoes = f"SELECT policial_id, compensacao, a_compensar FROM compensacoes WHERE {where_clause}"
            result_compensacoes = db_manager.execute_query(query_compensacoes, tuple(params))
            
            # Armazenar os resultados para referência
            self.result_compensacoes = result_compensacoes

            tabela.rows.clear()
            self.tabela_rows.clear()
            for idx, row in enumerate(result_compensacoes):
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
                
                compensacao_data = row["compensacao"] if hasattr(row, "keys") else row[1]
                a_compensar_data = row["a_compensar"] if hasattr(row, "keys") else row[2]
                
                dr = ft.DataRow(
                    selected=(self.selected_row_index == idx),
                    on_select_changed=on_row_select,
                    color=ft.Colors.GREY_200 if self.selected_row_index == idx else None,
                    cells=[
                        ft.DataCell(ft.Text(policial_nome_row)),
                        ft.DataCell(ft.Text(policial_matricula_row)),
                        ft.DataCell(ft.Text(formatar_data(compensacao_data))),
                        ft.DataCell(ft.Text(formatar_data(a_compensar_data))),
                    ]
                )
                tabela.rows.append(dr)
                self.tabela_rows.append(dr)
            tabela.update()

        field_policial.on_change = atualizar_tabela
        field_data_compensacao.on_change = atualizar_tabela
        field_data_a_compensar.on_change = atualizar_tabela

        # Função para apagar a compensação selecionada
        def apagar_compensacao(e):
            if self.selected_row_index is None:
                show_alert_dialog(e.control.page, "Selecione uma linha para apagar!", success=False)
                return
            
            # Obter os dados da compensação selecionada
            compensacao_selecionada = self.result_compensacoes[self.selected_row_index]
            
            # Criar diálogo de confirmação
            def confirmar_apagar(e):
                try:
                    # Construir a query de exclusão
                    policial_id = compensacao_selecionada["policial_id"] if hasattr(compensacao_selecionada, "keys") else compensacao_selecionada[0]
                    compensacao = compensacao_selecionada["compensacao"] if hasattr(compensacao_selecionada, "keys") else compensacao_selecionada[1]
                    a_compensar = compensacao_selecionada["a_compensar"] if hasattr(compensacao_selecionada, "keys") else compensacao_selecionada[2]
                    
                    # Query de exclusão
                    delete_query = """
                        DELETE FROM compensacoes 
                        WHERE policial_id = ? AND compensacao = ? AND a_compensar = ?
                    """
                    
                    # Executar a exclusão
                    success = self.app.db.execute_command(delete_query, (policial_id, compensacao, a_compensar))
                    
                    if success:
                        show_alert_dialog(e.control.page, "Compensação apagada com sucesso!", success=True)
                        # Limpar seleção
                        self.selected_row_index = None
                        # Atualizar a tabela
                        atualizar_tabela()
                    else:
                        show_alert_dialog(e.control.page, "Erro ao apagar a compensação!", success=False)
                        
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
                    f"Tem certeza que deseja apagar esta compensação?\n\n"
                    f"Data Compensação: {formatar_data(compensacao_selecionada['compensacao'] if hasattr(compensacao_selecionada, 'keys') else compensacao_selecionada[1])}\n"
                    f"Data A Compensar: {formatar_data(compensacao_selecionada['a_compensar'] if hasattr(compensacao_selecionada, 'keys') else compensacao_selecionada[2])}"
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
            on_click=apagar_compensacao
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