import flet as ft
from .base_screen import BaseScreen
from dialogalert import show_alert_dialog

class ConsultarPermutasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "consultar_permutas"

    def get_content(self) -> ft.Control:
        import datetime
        from database.database_manager import DatabaseManager

        titulo = ft.Text("Pesquisar Permutas Cadastradas", size=20,
                         weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER)

        txt_pesq_policial_solicitante = ft.TextButton(
            "Pesquise pela matrícula do solicitante:",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            )
        )
        field_policial_solicitante = ft.TextField(label="Matrícula Solicitante", width=200)
        col_policial_solicitante = ft.Column([txt_pesq_policial_solicitante, field_policial_solicitante], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        txt_pesq_policial_permutado = ft.TextButton(
            "Pesquise pela matrícula do permutado:",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            )
        )
        field_policial_permutado = ft.TextField(label="Matrícula Permutado", width=200)
        col_policial_permutado = ft.Column([txt_pesq_policial_permutado, field_policial_permutado], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        txt_pesq_data_permuta = ft.TextButton(
            "Pesquise por data da permuta:",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=lambda e: print("pesquisa por data da permuta")
        )
        field_data_permuta = ft.TextField(label="Data da Permuta", width=200, hint_text="dd/mm/aaaa")
        
        # Função para aplicar máscara de data
        def mascara_data_permuta(e):
            valor = ''.join([c for c in field_data_permuta.value if c.isdigit()])
            novo_valor = ''
            if len(valor) > 0:
                novo_valor += valor[:2]
            if len(valor) > 2:
                novo_valor += '/' + valor[2:4]
            if len(valor) > 4:
                novo_valor += '/' + valor[4:8]
            field_data_permuta.value = novo_valor
            e.control.page.update()
        
        col_data_permuta = ft.Column([txt_pesq_data_permuta, field_data_permuta], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        filtros_row = ft.Row([
            col_policial_solicitante,
            col_policial_permutado,
            col_data_permuta
        ], spacing=40, alignment=ft.MainAxisAlignment.CENTER)

        # Controle para seleção única e cor de linha
        self.selected_row_index = None
        self.tabela_rows = []  # Guardar referências das linhas
        self.result_permutas = []  # Guardar os dados das permutas para referência
        
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
                ft.DataColumn(ft.Text("Solicitante")),
                ft.DataColumn(ft.Text("Mat. Sol.")),
                ft.DataColumn(ft.Text("Permutado")),
                ft.DataColumn(ft.Text("Mat. Perm.")),
                ft.DataColumn(ft.Text("Data Solicitante")),
                ft.DataColumn(ft.Text("Data Permutado")),
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
            matricula_solicitante_val = field_policial_solicitante.value.strip()
            matricula_permutado_val = field_policial_permutado.value.strip()
            data_permuta_val = field_data_permuta.value.strip()
            
            policial_solicitante_id = None
            policial_solicitante_nome = ""
            policial_solicitante_matricula = ""
            policial_permutado_id = None
            policial_permutado_nome = ""
            policial_permutado_matricula = ""
            
            filtros = []
            params = []

            if matricula_solicitante_val:
                query_policial = "SELECT id, nome, matricula FROM policiais WHERE matricula = ?"
                result_policial = db_manager.execute_query(query_policial, (matricula_solicitante_val,))
                if result_policial:
                    policial_solicitante_id = result_policial[0]["id"] if hasattr(result_policial[0], "keys") else result_policial[0][0]
                    policial_solicitante_nome = result_policial[0]["nome"] if hasattr(result_policial[0], "keys") else result_policial[0][1]
                    policial_solicitante_matricula = result_policial[0]["matricula"] if hasattr(result_policial[0], "keys") else result_policial[0][2]
                    filtros.append("solicitante = ?")
                    params.append(policial_solicitante_id)

            if matricula_permutado_val:
                query_policial = "SELECT id, nome, matricula FROM policiais WHERE matricula = ?"
                result_policial = db_manager.execute_query(query_policial, (matricula_permutado_val,))
                if result_policial:
                    policial_permutado_id = result_policial[0]["id"] if hasattr(result_policial[0], "keys") else result_policial[0][0]
                    policial_permutado_nome = result_policial[0]["nome"] if hasattr(result_policial[0], "keys") else result_policial[0][1]
                    policial_permutado_matricula = result_policial[0]["matricula"] if hasattr(result_policial[0], "keys") else result_policial[0][2]
                    filtros.append("permutado = ?")
                    params.append(policial_permutado_id)

            if data_permuta_val and len(data_permuta_val) == 10:
                partes = data_permuta_val.split("/")
                if len(partes) == 3:
                    data_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
                    filtros.append("(date(data_solicitante) = ? OR date(data_permutado) = ?)")
                    params.extend([data_sql, data_sql])

            where_clause = " AND ".join(filtros) if filtros else "1=1"
            query_permutas = f"SELECT solicitante, permutado, data_solicitante, data_permutado FROM permutas WHERE {where_clause}"
            result_permutas = db_manager.execute_query(query_permutas, tuple(params))
            
            # Armazenar os resultados para referência
            self.result_permutas = result_permutas

            tabela.rows.clear()
            self.tabela_rows.clear()
            for idx, row in enumerate(result_permutas):
                # Nomes e matrículas dos policiais
                nome_solicitante_row = policial_solicitante_nome
                matricula_solicitante_row = policial_solicitante_matricula
                nome_permutado_row = policial_permutado_nome
                matricula_permutado_row = policial_permutado_matricula
                
                # Se não temos os dados do solicitante, buscar
                if not nome_solicitante_row:
                    query_nome = "SELECT nome, matricula FROM policiais WHERE id = ?"
                    res_nome = db_manager.execute_query(query_nome, (row["solicitante"],)) if hasattr(row, "keys") else db_manager.execute_query(query_nome, (row[0],))
                    if res_nome:
                        nome_solicitante_row = res_nome[0]["nome"] if hasattr(res_nome[0], "keys") else res_nome[0][0]
                        matricula_solicitante_row = res_nome[0]["matricula"] if hasattr(res_nome[0], "keys") else res_nome[0][1]
                
                # Se não temos os dados do permutado, buscar
                if not nome_permutado_row:
                    query_nome = "SELECT nome, matricula FROM policiais WHERE id = ?"
                    res_nome = db_manager.execute_query(query_nome, (row["permutado"],)) if hasattr(row, "keys") else db_manager.execute_query(query_nome, (row[1],))
                    if res_nome:
                        nome_permutado_row = res_nome[0]["nome"] if hasattr(res_nome[0], "keys") else res_nome[0][0]
                        matricula_permutado_row = res_nome[0]["matricula"] if hasattr(res_nome[0], "keys") else res_nome[0][1]
                
                # Converter datas para formato brasileiro
                def formatar_data(data_sql):
                    try:
                        from datetime import datetime
                        data_obj = datetime.strptime(data_sql, "%Y-%m-%d")
                        return data_obj.strftime("%d/%m/%Y")
                    except:
                        return data_sql
                
                data_solicitante = row["data_solicitante"] if hasattr(row, "keys") else row[2]
                data_permutado = row["data_permutado"] if hasattr(row, "keys") else row[3]
                
                dr = ft.DataRow(
                    selected=(self.selected_row_index == idx),
                    on_select_changed=on_row_select,
                    color=ft.Colors.GREY_200 if self.selected_row_index == idx else None,
                    cells=[
                        ft.DataCell(ft.Text(nome_solicitante_row)),
                        ft.DataCell(ft.Text(matricula_solicitante_row)),
                        ft.DataCell(ft.Text(nome_permutado_row)),
                        ft.DataCell(ft.Text(matricula_permutado_row)),
                        ft.DataCell(ft.Text(formatar_data(data_solicitante))),
                        ft.DataCell(ft.Text(formatar_data(data_permutado))),
                    ]
                )
                tabela.rows.append(dr)
                self.tabela_rows.append(dr)
            tabela.update()

        field_policial_solicitante.on_change = atualizar_tabela
        field_policial_permutado.on_change = atualizar_tabela
        
        # Função combinada para aplicar máscara e atualizar tabela
        def mascara_e_atualizar(e):
            mascara_data_permuta(e)
            atualizar_tabela()
        
        field_data_permuta.on_change = mascara_e_atualizar

        # Função para apagar a permuta selecionada
        def apagar_permuta(e):
            if self.selected_row_index is None:
                show_alert_dialog(e.control.page, "Selecione uma linha para apagar!", success=False)
                return
            
            # Obter os dados da permuta selecionada
            permuta_selecionada = self.result_permutas[self.selected_row_index]
            
            # Criar diálogo de confirmação
            def confirmar_apagar(e):
                try:
                    # Construir a query de exclusão
                    solicitante_id = permuta_selecionada["solicitante"] if hasattr(permuta_selecionada, "keys") else permuta_selecionada[0]
                    permutado_id = permuta_selecionada["permutado"] if hasattr(permuta_selecionada, "keys") else permuta_selecionada[1]
                    data_solicitante = permuta_selecionada["data_solicitante"] if hasattr(permuta_selecionada, "keys") else permuta_selecionada[2]
                    data_permutado = permuta_selecionada["data_permutado"] if hasattr(permuta_selecionada, "keys") else permuta_selecionada[3]
                    
                    # Query de exclusão
                    delete_query = """
                        DELETE FROM permutas 
                        WHERE solicitante = ? AND permutado = ? AND data_solicitante = ? AND data_permutado = ?
                    """
                    
                    # Executar a exclusão
                    success = self.app.db.execute_command(delete_query, (solicitante_id, permutado_id, data_solicitante, data_permutado))
                    
                    if success:
                        show_alert_dialog(e.control.page, "Permuta apagada com sucesso!", success=True)
                        # Limpar seleção
                        self.selected_row_index = None
                        # Atualizar a tabela
                        atualizar_tabela()
                    else:
                        show_alert_dialog(e.control.page, "Erro ao apagar a permuta!", success=False)
                        
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
                    f"Tem certeza que deseja apagar esta permuta?\n\n"
                    f"Data Solicitante: {formatar_data(permuta_selecionada['data_solicitante'] if hasattr(permuta_selecionada, 'keys') else permuta_selecionada[2])}\n"
                    f"Data Permutado: {formatar_data(permuta_selecionada['data_permutado'] if hasattr(permuta_selecionada, 'keys') else permuta_selecionada[3])}"
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
            on_click=apagar_permuta
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
            # btn_editar,
            # btn_gravar
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
