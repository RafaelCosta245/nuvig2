import flet as ft
from .base_screen import BaseScreen
from dialogalert import show_alert_dialog

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
        field_data = ft.TextField(label="Data", width=200, hint_text="dd/mm/aaaa")
        
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
        db_manager = self.app.db
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

        # Controle para seleção única e cor de linha
        self.selected_row_index = None
        self.tabela_rows = []  # Guardar referências das linhas
        self.result_extras = []  # Guardar os dados das extras para referência
        
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
                ft.DataColumn(ft.Text("Intertício")),
                ft.DataColumn(ft.Text("Data")),
                ft.DataColumn(ft.Text("Policial")),
                ft.DataColumn(ft.Text("Turno")),
                ft.DataColumn(ft.Text("Operação")),
                ft.DataColumn(ft.Text("Início")),
                ft.DataColumn(ft.Text("Fim")),
                ft.DataColumn(ft.Text("Quant. Horas")),
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
                    policial_nome = result_policial[0]["nome"] if hasattr(result_policial[0], "keys") else result_policial[0][0]
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
            
            # Armazenar os resultados para referência
            self.result_extras = result_extras

            tabela.rows.clear()
            self.tabela_rows.clear()
            for idx, row in enumerate(result_extras):
                policial_nome_row = policial_nome
                if not policial_nome_row:
                    query_nome = "SELECT nome FROM policiais WHERE id = ?"
                    res_nome = db_manager.execute_query(query_nome, (row["policial_id"],)) if hasattr(row, "keys") else db_manager.execute_query(query_nome, (row[2],))
                    policial_nome_row = res_nome[0]["nome"] if res_nome and hasattr(res_nome[0], "keys") else (res_nome[0][0] if res_nome else "")
                query_data_val = "SELECT data FROM calendario WHERE id = ?"
                res_data_val = db_manager.execute_query(query_data_val, (row["data_id"],)) if hasattr(row, "keys") else db_manager.execute_query(query_data_val, (row[1],))
                data_val_row = res_data_val[0]["data"] if res_data_val and hasattr(res_data_val[0], "keys") else (res_data_val[0][0] if res_data_val else "")
                dr = ft.DataRow(
                    selected=(self.selected_row_index == idx),
                    on_select_changed=on_row_select,
                    color=ft.Colors.GREY_200 if self.selected_row_index == idx else None,
                    cells=[
                        ft.DataCell(ft.Text(row["interticio"] if hasattr(row, "keys") else row[0])),
                        ft.DataCell(ft.Text(data_val_row)),
                        ft.DataCell(ft.Text(policial_nome_row)),
                        ft.DataCell(ft.Text(row["turno"] if hasattr(row, "keys") else row[3])),
                        ft.DataCell(ft.Text(row["operacao"] if hasattr(row, "keys") else row[4])),
                        ft.DataCell(ft.Text(row["inicio"] if hasattr(row, "keys") else row[5])),
                        ft.DataCell(ft.Text(row["fim"] if hasattr(row, "keys") else row[6])),
                        ft.DataCell(ft.Text(row["horas"] if hasattr(row, "keys") else row[7])),
                    ]
                )
                tabela.rows.append(dr)
                self.tabela_rows.append(dr)
            tabela.update()
            # Não fechar a conexão global do app

        field_policial.on_change = atualizar_tabela
        
        # Função combinada para aplicar máscara e atualizar tabela
        def mascara_e_atualizar(e):
            mascara_data(e)
            atualizar_tabela()
        
        field_data.on_change = mascara_e_atualizar
        field_interticio.on_change = atualizar_tabela

        # Função para apagar a extra selecionada
        def apagar_extra(e):
            if self.selected_row_index is None:
                show_alert_dialog(e.control.page, "Selecione uma linha para apagar!", success=False)
                return
            
            # Obter os dados da extra selecionada
            extra_selecionada = self.result_extras[self.selected_row_index]
            
            # Criar diálogo de confirmação
            def confirmar_apagar(e):
                try:
                    # Construir a query de exclusão
                    # Precisamos de uma chave única para identificar a extra
                    # Vamos usar a combinação de policial_id, data_id, turno, operacao e inicio
                    policial_id = extra_selecionada["policial_id"] if hasattr(extra_selecionada, "keys") else extra_selecionada[2]
                    data_id = extra_selecionada["data_id"] if hasattr(extra_selecionada, "keys") else extra_selecionada[1]
                    turno = extra_selecionada["turno"] if hasattr(extra_selecionada, "keys") else extra_selecionada[3]
                    operacao = extra_selecionada["operacao"] if hasattr(extra_selecionada, "keys") else extra_selecionada[4]
                    inicio = extra_selecionada["inicio"] if hasattr(extra_selecionada, "keys") else extra_selecionada[5]
                    
                    # Query de exclusão
                    delete_query = """
                        DELETE FROM extras 
                        WHERE policial_id = ? AND data_id = ? AND turno = ? AND operacao = ? AND inicio = ?
                    """
                    
                    # Executar a exclusão
                    success = self.app.db.execute_command(delete_query, (policial_id, data_id, turno, operacao, inicio))
                    
                    if success:
                        show_alert_dialog(e.control.page, "Extra apagada com sucesso!", success=True)
                        # Limpar seleção
                        self.selected_row_index = None
                        # Atualizar a tabela
                        atualizar_tabela()
                    else:
                        show_alert_dialog(e.control.page, "Erro ao apagar a extra!", success=False)
                        
                except Exception as ex:
                    show_alert_dialog(e.control.page, f"Erro ao apagar: {str(ex)}", success=False)
                
                # Fechar o diálogo
                e.control.page.close(dlg_confirmacao)
            
            def cancelar_apagar(e):
                e.control.page.close(dlg_confirmacao)
            
            # Criar o diálogo de confirmação
            dlg_confirmacao = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmar Exclusão", color=ft.Colors.RED),
                content=ft.Text(
                    f"Tem certeza que deseja apagar esta extra?\n\n"
                    f"Intertício: {extra_selecionada['interticio'] if hasattr(extra_selecionada, 'keys') else extra_selecionada[0]}\n"
                    f"Turno: {extra_selecionada['turno'] if hasattr(extra_selecionada, 'keys') else extra_selecionada[3]}\n"
                    f"Operação: {extra_selecionada['operacao'] if hasattr(extra_selecionada, 'keys') else extra_selecionada[4]}\n"
                    f"Início: {extra_selecionada['inicio'] if hasattr(extra_selecionada, 'keys') else extra_selecionada[5]}"
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
            on_click=apagar_extra
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
