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
        field_policial = ft.TextField(label="Matrícula", width=200, max_length=8)
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
                ft.DataColumn(ft.Text("QRA", text_align=ft.TextAlign.LEFT)),
                ft.DataColumn(ft.Text("Matrícula", text_align=ft.TextAlign.LEFT)),
                ft.DataColumn(ft.Text("Período 1", text_align=ft.TextAlign.LEFT)),
                ft.DataColumn(ft.Text("Período 2", text_align=ft.TextAlign.LEFT)),
                ft.DataColumn(ft.Text("Período 3", text_align=ft.TextAlign.LEFT)),
                ft.DataColumn(ft.Text("Total Dias", text_align=ft.TextAlign.LEFT)),
                ft.DataColumn(ft.Text("Conflitos", text_align=ft.TextAlign.LEFT)),
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

        def verificar_conflitos_ferias():
            """
            Verifica conflitos de datas entre policiais da mesma equipe
            Retorna um dicionário com informações de conflitos para cada linha da tabela
            IMPORTANTE: Sempre busca TODOS os dados do banco para detectar conflitos reais
            """
            conflitos_por_linha = {}
            
            try:
                db_manager = self.app.db
                
                # SEMPRE buscar TODAS as férias do banco para detectar conflitos reais
                # Os conflitos são uma propriedade objetiva dos dados, não da visualização
                query_completa = """
                    SELECT f.policial_id, f.periodo_aquisitivo, f.inicio1, f.fim1, f.inicio2, f.fim2, f.inicio3, f.fim3,
                           p.qra, p.matricula, p.escala
                    FROM ferias f
                    JOIN policiais p ON f.policial_id = p.id
                """
                todas_ferias = db_manager.execute_query(query_completa)
                
                if not todas_ferias:
                    return conflitos_por_linha
                
                # Criar um dicionário para mapear conflitos por policial_id + periodo_aquisitivo + inicio1
                conflitos_por_ferias = {}
                
                # Para cada linha de férias, verificar conflitos com outros policiais da mesma equipe
                for i, ferias_atual in enumerate(todas_ferias):
                    policial_id_atual = ferias_atual["policial_id"] if hasattr(ferias_atual, "keys") else ferias_atual[0]
                    escala_atual = ferias_atual["escala"] if hasattr(ferias_atual, "keys") else ferias_atual[9]
                    equipe_atual = escala_atual[0] if escala_atual else ""
                    
                    conflitos_linha = []
                    
                    # Verificar conflitos com outros policiais da mesma equipe
                    for j, ferias_outro in enumerate(todas_ferias):
                        if i == j:  # Não comparar com ele mesmo
                            continue
                            
                        policial_id_outro = ferias_outro["policial_id"] if hasattr(ferias_outro, "keys") else ferias_outro[0]
                        escala_outro = ferias_outro["escala"] if hasattr(ferias_outro, "keys") else ferias_outro[9]
                        equipe_outro = escala_outro[0] if escala_outro else ""
                        
                        # Só verificar se for da mesma equipe
                        if equipe_atual != equipe_outro:
                            continue
                        
                        qra_outro = ferias_outro["qra"] if hasattr(ferias_outro, "keys") else ferias_outro[8]
                        
                        # Verificar conflitos entre os períodos
                        conflito = verificar_conflito_periodos(ferias_atual, ferias_outro, qra_outro)
                        if conflito:
                            conflitos_linha.append(conflito)
                    
                    if conflitos_linha:
                        # Criar chave única para esta férias: policial_id + periodo_aquisitivo + inicio1
                        periodo_aquisitivo = ferias_atual["periodo_aquisitivo"] if hasattr(ferias_atual, "keys") else ferias_atual[1]
                        inicio1 = ferias_atual["inicio1"] if hasattr(ferias_atual, "keys") else ferias_atual[2]
                        chave_ferias = f"{policial_id_atual}_{periodo_aquisitivo}_{inicio1}"
                        conflitos_por_ferias[chave_ferias] = conflitos_linha
                
                return conflitos_por_ferias
                
            except Exception as e:
                print(f"Erro ao verificar conflitos: {e}")
                return conflitos_por_ferias

        def verificar_conflito_periodos(ferias1, ferias2, qra_policial2):
            """
            Verifica se há conflito entre os períodos de duas férias
            """
            try:
                from datetime import datetime
                
                # Extrair períodos da primeira férias
                periodos1 = []
                if ferias1["inicio1"] and ferias1["fim1"]:
                    periodos1.append(("Período 1", ferias1["inicio1"], ferias1["fim1"]))
                if ferias1["inicio2"] and ferias1["fim2"]:
                    periodos1.append(("Período 2", ferias1["inicio2"], ferias1["fim2"]))
                if ferias1["inicio3"] and ferias1["fim3"]:
                    periodos1.append(("Período 3", ferias1["inicio3"], ferias1["fim3"]))
                
                # Extrair períodos da segunda férias
                periodos2 = []
                if ferias2["inicio1"] and ferias2["fim1"]:
                    periodos2.append(("Período 1", ferias2["inicio1"], ferias2["fim1"]))
                if ferias2["inicio2"] and ferias2["fim2"]:
                    periodos2.append(("Período 2", ferias2["inicio2"], ferias2["fim2"]))
                if ferias2["inicio3"] and ferias2["fim3"]:
                    periodos2.append(("Período 3", ferias2["inicio3"], ferias2["fim3"]))
                
                # Verificar conflitos entre os períodos
                for periodo1_nome, inicio1, fim1 in periodos1:
                    for periodo2_nome, inicio2, fim2 in periodos2:
                        # Converter para datetime
                        inicio1_dt = datetime.strptime(inicio1, "%Y-%m-%d")
                        fim1_dt = datetime.strptime(fim1, "%Y-%m-%d")
                        inicio2_dt = datetime.strptime(inicio2, "%Y-%m-%d")
                        fim2_dt = datetime.strptime(fim2, "%Y-%m-%d")
                        
                        # Verificar sobreposição
                        if not (fim1_dt < inicio2_dt or inicio1_dt > fim2_dt):
                            # Há conflito - calcular período de conflito
                            data_inicio_conflito = max(inicio1_dt, inicio2_dt)
                            data_fim_conflito = min(fim1_dt, fim2_dt)
                            
                            return {
                                "policial": qra_policial2,
                                "periodo_atual": periodo1_nome,
                                "periodo_conflito": periodo2_nome,
                                "data_inicio": data_inicio_conflito.strftime("%d/%m/%Y"),
                                "data_fim": data_fim_conflito.strftime("%d/%m/%Y")
                            }
                
                return None
                
            except Exception as e:
                print(f"Erro ao verificar conflito de períodos: {e}")
                return None

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
            
            # Verificar conflitos de datas
            conflitos = verificar_conflitos_ferias()
            
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
                policial_qra_row = policial_nome  # Usar o nome como fallback se não encontrar QRA
                policial_matricula_row = policial_matricula
                if not policial_qra_row:
                    query_policial_info = "SELECT qra, matricula FROM policiais WHERE id = ?"
                    res_policial = db_manager.execute_query(query_policial_info, (row["policial_id"],)) if hasattr(row, "keys") else db_manager.execute_query(query_policial_info, (row[0],))
                    if res_policial:
                        policial_qra_row = res_policial[0]["qra"] if hasattr(res_policial[0], "keys") else res_policial[0][0]
                        policial_matricula_row = res_policial[0]["matricula"] if hasattr(res_policial[0], "keys") else res_policial[0][1]
                
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
                
                # Verificar se esta linha tem conflitos
                # Criar chave única para esta férias: policial_id + periodo_aquisitivo + inicio1
                policial_id_row = row["policial_id"] if hasattr(row, "keys") else row[0]
                periodo_aquisitivo_row = row["periodo_aquisitivo"] if hasattr(row, "keys") else row[1]
                inicio1_row = row["inicio1"] if hasattr(row, "keys") else row[2]
                chave_ferias = f"{policial_id_row}_{periodo_aquisitivo_row}_{inicio1_row}"
                
                tem_conflito = chave_ferias in conflitos
                cor_linha = None
                indicador_conflito = ""
                
                if tem_conflito:
                    # Criar indicador de conflito com quebra de linha (sem destaque amarelo)
                    conflitos_linha = conflitos[chave_ferias]
                    indicadores = []
                    for conflito in conflitos_linha:
                        indicadores.append(f"⚠️ {conflito['policial']} ({conflito['periodo_conflito']})")
                    indicador_conflito = "\n".join(indicadores)
                
                # Aplicar cor de seleção se a linha estiver selecionada
                if self.selected_row_index == idx:
                    cor_linha = ft.Colors.GREY_200
                
                # Criar células da tabela com larguras otimizadas e texto alinhado à esquerda
                celulas = [
                    ft.DataCell(
                        ft.Text(policial_qra_row, no_wrap=True, text_align=ft.TextAlign.LEFT)
                    ),
                    ft.DataCell(
                        ft.Text(policial_matricula_row, no_wrap=True, text_align=ft.TextAlign.LEFT)
                    ),
                    ft.DataCell(
                        ft.Text(formatar_periodo(inicio1, fim1), no_wrap=True, text_align=ft.TextAlign.LEFT)
                    ),
                    ft.DataCell(
                        ft.Text(formatar_periodo(inicio2, fim2), no_wrap=True, text_align=ft.TextAlign.LEFT)
                    ),
                    ft.DataCell(
                        ft.Text(formatar_periodo(inicio3, fim3), no_wrap=True, text_align=ft.TextAlign.LEFT)
                    ),
                    ft.DataCell(
                        ft.Text(f"{total_dias} dias", no_wrap=True, text_align=ft.TextAlign.LEFT)
                    ),
                    ft.DataCell(
                        ft.Text(
                            indicador_conflito if indicador_conflito else "-", 
                            color=ft.Colors.RED if indicador_conflito else ft.Colors.BLACK, 
                            size=10,
                            no_wrap=False,  # Permite quebra de linha apenas aqui
                            text_align=ft.TextAlign.LEFT
                        )
                    ),
                ]
                
                dr = ft.DataRow(
                    selected=(self.selected_row_index == idx),
                    on_select_changed=on_row_select,
                    color=cor_linha,
                    cells=celulas
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
        # Função para editar as férias selecionadas
        def editar_ferias(e):
            if self.selected_row_index is None:
                show_alert_dialog(e.control.page, "Selecione uma linha para editar!", success=False)
                return
            
            # Obter os dados das férias selecionadas
            ferias_selecionada = self.result_ferias[self.selected_row_index]
            
            # Obter dados para o diálogo
            if hasattr(ferias_selecionada, "keys"):
                policial_id = ferias_selecionada["policial_id"]
                periodo_aquisitivo = ferias_selecionada["periodo_aquisitivo"]
                inicio1 = ferias_selecionada["inicio1"]
                fim1 = ferias_selecionada["fim1"]
                inicio2 = ferias_selecionada["inicio2"]
                fim2 = ferias_selecionada["fim2"]
                inicio3 = ferias_selecionada["inicio3"]
                fim3 = ferias_selecionada["fim3"]
            else:
                policial_id = ferias_selecionada[0]
                periodo_aquisitivo = ferias_selecionada[1]
                inicio1 = ferias_selecionada[2]
                fim1 = ferias_selecionada[3]
                inicio2 = ferias_selecionada[4]
                fim2 = ferias_selecionada[5]
                inicio3 = ferias_selecionada[6]
                fim3 = ferias_selecionada[7]
            
            # Obter nome do policial
            query_nome = "SELECT nome FROM policiais WHERE id = ?"
            res_nome = self.app.db.execute_query(query_nome, (policial_id,))
            policial_nome = res_nome[0]["nome"] if res_nome and hasattr(res_nome[0], "keys") else res_nome[0][0] if res_nome else "Desconhecido"
            
            # Função para converter data do formato SQL para DD/MM/YYYY
            def sql_to_display_date(sql_date):
                if not sql_date:
                    return ""
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(sql_date, "%Y-%m-%d")
                    return date_obj.strftime("%d/%m/%Y")
                except:
                    return sql_date
            
            # Campos de entrada para edição
            field_periodo_aquisitivo = ft.TextField(
                label="Período Aquisitivo",
                value=str(periodo_aquisitivo),
                width=200
            )
            
            field_inicio1 = ft.TextField(
                label="Início Período 1",
                value=sql_to_display_date(inicio1),
                width=200,
                hint_text="DD/MM/YYYY"
            )
            
            field_fim1 = ft.TextField(
                label="Fim Período 1",
                value=sql_to_display_date(fim1),
                width=200,
                hint_text="DD/MM/YYYY"
            )
            
            field_inicio2 = ft.TextField(
                label="Início Período 2",
                value=sql_to_display_date(inicio2),
                width=200,
                hint_text="DD/MM/YYYY"
            )
            
            field_fim2 = ft.TextField(
                label="Fim Período 2",
                value=sql_to_display_date(fim2),
                width=200,
                hint_text="DD/MM/YYYY"
            )
            
            field_inicio3 = ft.TextField(
                label="Início Período 3",
                value=sql_to_display_date(inicio3),
                width=200,
                hint_text="DD/MM/YYYY"
            )
            
            field_fim3 = ft.TextField(
                label="Fim Período 3",
                value=sql_to_display_date(fim3),
                width=200,
                hint_text="DD/MM/YYYY"
            )
            
            # Função para converter data do formato DD/MM/YYYY para SQL
            def display_to_sql_date(display_date):
                if not display_date or display_date.strip() == "":
                    return None
                try:
                    from datetime import datetime
                    date_obj = datetime.strptime(display_date.strip(), "%d/%m/%Y")
                    return date_obj.strftime("%Y-%m-%d")
                except:
                    return None
            
            # Função para calcular dias entre duas datas (mesma função do cadastro)
            def calcular_dias_edicao(data_inicio, data_fim):
                if not data_inicio or not data_fim:
                    return 0
                try:
                    from datetime import datetime
                    inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
                    fim = datetime.strptime(data_fim, "%d/%m/%Y")
                    return (fim - inicio).days + 1  # +1 porque inclui ambos os dias
                except:
                    return 0
            
            # Função para mostrar erro de período (mesma do cadastro)
            def mostrar_erro_periodo_edicao(page):
                def fechar_dialogo(e):
                    page.close(dialogo_erro)
                
                dialogo_erro = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Período de Férias Inválido", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                    content=ft.Text(
                        "O total de dias de férias deve ser exatamente 30 dias.\n\n"
                        "Você pode dividir em:\n"
                        "• 1 período de 30 dias\n"
                        "• 2 períodos de 15 dias cada\n"
                        "• 3 períodos de 10 dias cada\n",
                        size=14
                    ),
                    actions=[
                        ft.TextButton("Entendi", on_click=fechar_dialogo)
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                page.open(dialogo_erro)
            
            # Função para salvar as alterações
            def salvar_alteracoes(e):
                try:
                    # Validar período aquisitivo
                    if not field_periodo_aquisitivo.value.strip():
                        show_alert_dialog(e.control.page, "Período aquisitivo é obrigatório!", success=False)
                        return
                    
                    # Validar se pelo menos o período 1 foi preenchido
                    if not field_inicio1.value.strip() or not field_fim1.value.strip():
                        show_alert_dialog(e.control.page, "Período 1 é obrigatório!", success=False)
                        return
                    
                    # Calcular dias de cada período (usando formato DD/MM/YYYY)
                    dias_periodo1 = calcular_dias_edicao(field_inicio1.value, field_fim1.value)
                    dias_periodo2 = calcular_dias_edicao(field_inicio2.value, field_fim2.value) if field_inicio2.value and field_fim2.value else 0
                    dias_periodo3 = calcular_dias_edicao(field_inicio3.value, field_fim3.value) if field_inicio3.value and field_fim3.value else 0
                    total_dias = dias_periodo1 + dias_periodo2 + dias_periodo3
                    
                    # Validar se o total é exatamente 30 dias (mesma validação do cadastro)
                    if total_dias != 30:
                        mostrar_erro_periodo_edicao(e.control.page)
                        return
                    
                    # Converter datas para formato SQL
                    novo_inicio1 = display_to_sql_date(field_inicio1.value)
                    novo_fim1 = display_to_sql_date(field_fim1.value)
                    novo_inicio2 = display_to_sql_date(field_inicio2.value)
                    novo_fim2 = display_to_sql_date(field_fim2.value)
                    novo_inicio3 = display_to_sql_date(field_inicio3.value)
                    novo_fim3 = display_to_sql_date(field_fim3.value)
                    
                    # Query de atualização
                    update_query = """
                        UPDATE ferias 
                        SET periodo_aquisitivo = ?, 
                            inicio1 = ?, fim1 = ?, 
                            inicio2 = ?, fim2 = ?, 
                            inicio3 = ?, fim3 = ?
                        WHERE policial_id = ? AND periodo_aquisitivo = ? AND inicio1 = ?
                    """
                    
                    # Executar a atualização
                    success = self.app.db.execute_command(
                        update_query, 
                        (
                            field_periodo_aquisitivo.value.strip(),
                            novo_inicio1, novo_fim1,
                            novo_inicio2, novo_fim2,
                            novo_inicio3, novo_fim3,
                            policial_id, periodo_aquisitivo, inicio1
                        )
                    )
                    
                    if success:
                        show_alert_dialog(e.control.page, "Férias atualizadas com sucesso!", success=True)
                        # Atualizar a tabela
                        atualizar_tabela()
                    else:
                        show_alert_dialog(e.control.page, "Erro ao atualizar as férias!", success=False)
                        
                except Exception as ex:
                    show_alert_dialog(e.control.page, f"Erro ao salvar: {str(ex)}", success=False)
                
                # Fechar o diálogo
                e.control.page.close(dlg_edicao)
            
            def cancelar_edicao(e):
                e.control.page.close(dlg_edicao)
            
            # Criar o diálogo de edição
            dlg_edicao = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar Férias", color=ft.Colors.BLACK),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text(f"Policial: {policial_nome}", weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        field_periodo_aquisitivo,
                        ft.Container(height=8),
                        ft.Row([field_inicio1, field_fim1], spacing=10),
                        ft.Container(height=8),
                        ft.Row([field_inicio2, field_fim2], spacing=10),
                        ft.Container(height=8),
                        ft.Row([field_inicio3, field_fim3], spacing=10),
                        ft.Container(height=10),
                    ], scroll=ft.ScrollMode.AUTO),
                    width=500,
                    height=450,
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=cancelar_edicao),
                    ft.TextButton("Salvar", on_click=salvar_alteracoes, style=ft.ButtonStyle(color=ft.Colors.GREEN)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            e.control.page.open(dlg_edicao)

        btn_editar = ft.TextButton(
            "Editar",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12)
            ),
            on_click=editar_ferias
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
