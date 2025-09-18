import flet as ft
from .base_screen import BaseScreen
from dialogalert import show_alert_dialog

class CadastrarExtraScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "cadastrar_extra"

    def get_content(self) -> ft.Control:
        # Campos do formulário
        matricula = ft.TextField(label="Matrícula", width=200, max_length=8)
        policial = ft.TextField(label="Policial", width=200, read_only=True)
        data = ft.TextField(label="Data", width=200, hint_text="dd/mm/aaaa")
        operacao = ft.Dropdown(
            label="Operação",
            width=200,
            options=[
                ft.dropdown.Option("Rotina"),
                ft.dropdown.Option("OBLL"),
                ft.dropdown.Option("Outro"),
            ]
        )
        turno = ft.Dropdown(
            label="Turno",
            width=200,
            options=[
                ft.dropdown.Option("Diurno"),
                ft.dropdown.Option("Noturno"),
                ft.dropdown.Option("Vespertino"),
            ]
        )
        inicio = ft.TextField(label="Início", width=200, hint_text="hh:mm")
        fim = ft.TextField(label="Fim", width=200, hint_text="hh:mm")
        quant_horas = ft.TextField(label="Quant. Horas", width=200)
        # horas_disp = ft.Text(value="Horas disponíveis", text_align=ft.TextAlign.LEFT)
        # interticio = ft.Text(value="Interticio:", text_align=ft.TextAlign.LEFT)
        horas_disp = ft.Text(value='Disponíveis:',weight=ft.FontWeight.BOLD, size=14 )
        interticio = ft.Text(value="Intertício:",weight=ft.FontWeight.BOLD, size=14)
        
        # Text widget para mostrar as horas disponíveis (será atualizado dinamicamente)
        horas_disp_text = ft.Text(value='0 horas', weight=ft.FontWeight.BOLD, size=14)
        
        c_horas_disp = ft.Container(
            content=ft.Row(
                controls=[horas_disp, horas_disp_text],
                alignment=ft.MainAxisAlignment.CENTER),
            #alignment=ft.alignment.Alignment(-0.5, 0),
            alignment=ft.alignment.center,
            width=inicio.width,
            height=inicio.height,
            #bgcolor=ft.Colors.ORANGE,
        )
        interticio_val = ft.Text(value="", weight=ft.FontWeight.BOLD, size=14)
        
        def calcular_horas_disponiveis():
            """Calcula as horas disponíveis baseado no intertício e operação atual"""
            try:
                # 1. Buscar ID do intertício pelo nome
                interticio_nome = interticio_val.value.strip()
                if not interticio_nome:
                    horas_disp_text.value = "0 horas"
                    return
                
                query_interticio_id = "SELECT id FROM interticios WHERE nome = ?"
                result_interticio_id = self.app.db.execute_query(query_interticio_id, (interticio_nome,))
                if not result_interticio_id:
                    horas_disp_text.value = "986 horas"
                    return
                
                interticio_id = result_interticio_id[0]["id"]
                
                # 2. Buscar soma das horas na tabela horasextras
                operacao_val = operacao.value if operacao.value else ""
                if operacao_val:
                    query_horasextras = """
                        SELECT SUM(qty_horas) as total_horas 
                        FROM horasextras 
                        WHERE interticio_id = ? AND tipo = ?
                    """
                    result_horasextras = self.app.db.execute_query(query_horasextras, (interticio_id, operacao_val))
                    total_horasextras = result_horasextras[0]["total_horas"] if result_horasextras and result_horasextras[0]["total_horas"] else 0
                else:
                    total_horasextras = 0
                
                # 3. Buscar soma das horas na tabela extras
                if operacao_val:
                    query_extras = """
                        SELECT SUM(horas) as total_horas 
                        FROM extras 
                        WHERE interticio = ? AND operacao = ?
                    """
                    result_extras = self.app.db.execute_query(query_extras, (interticio_nome, operacao_val))
                    total_extras = result_extras[0]["total_horas"] if result_extras and result_extras[0]["total_horas"] else 0
                else:
                    total_extras = 0
                
                # 4. Calcular diferença: horasextras - extras
                horas_disponiveis = total_horasextras - total_extras
                
                # 5. Atualizar o texto das horas disponíveis
                horas_disp_text.value = f"{horas_disponiveis} horas"
                
            except Exception as e:
                print(f"Erro ao calcular horas disponíveis: {e}")
                horas_disp_text.value = "0 horas"
        
        def atualizar_interticio(e=None):
            val = data.value.strip()
            if len(val) == 10 and '/' in val:
                partes = val.split("/")
                data_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
                query_interticio = (
                    "SELECT nome FROM interticios "
                    "WHERE date(?) BETWEEN date(data_inicial) AND date(data_final) LIMIT 1"
                )
                result_interticio = self.app.db.execute_query(query_interticio, (data_sql,))
                if result_interticio and len(result_interticio) > 0:
                    if isinstance(result_interticio[0], dict) or hasattr(result_interticio[0], "keys"):
                        interticio_nome = result_interticio[0]["nome"]
                    else:
                        interticio_nome = result_interticio[0][0]
                    interticio_val.value = interticio_nome
                else:
                    interticio_val.value = ""
            else:
                interticio_val.value = ""
            
            # Calcular horas disponíveis quando o intertício for atualizado
            calcular_horas_disponiveis()
            
            if e:
                e.control.page.update()
        data.on_change = atualizar_interticio
        atualizar_interticio()
        c_interticio = ft.Container(
            content=ft.Row(
                controls=[interticio, interticio_val],
                alignment=ft.MainAxisAlignment.CENTER)
            ,
            width=inicio.width,
            height=inicio.height,
            alignment=ft.alignment.center,
        )


        # Função para aplicar máscara de data
        def mascara_data(e):
            valor = ''.join([c for c in data.value if c.isdigit()])
            novo_valor = ''
            if len(valor) > 0:
                novo_valor += valor[:2]
            if len(valor) > 2:
                novo_valor += '/' + valor[2:4]
            if len(valor) > 4:
                novo_valor += '/' + valor[4:8]
            data.value = novo_valor
            atualizar_interticio()
            e.control.page.update()
        data.on_change = mascara_data

        # Função para buscar policial pela matrícula
        def buscar_policial(e):
            valor = matricula.value.strip()
            if valor:
                policial_info = self.app.db.get_policial_by_matricula(valor)
                policial.value = policial_info["qra"] if policial_info and "qra" in policial_info else ""
            else:
                policial.value = ""
            e.control.page.update()
        matricula.on_change = buscar_policial

        # Função para lógica do dropdown operação
        def on_operacao_change(e):
            if operacao.value == "OBLL":
                turno.value = "Vespertino"
                quant_horas.value = "12"
                inicio.value = "16:00"
                fim.value = "04:00"
            
            # Calcular horas disponíveis quando a operação mudar
            calcular_horas_disponiveis()
            
            e.control.page.update()
        operacao.on_change = on_operacao_change

        # Função para lógica do dropdown turno
        def on_turno_change(e):
            if turno.value == "Diurno":
                quant_horas.value = "12"
                inicio.value = "08:00"
                fim.value = "20:00"
                if operacao.value == "OBLL":
                    operacao.value = "Guarda"
            elif turno.value == "Noturno":
                quant_horas.value = "12"
                inicio.value = "20:00"
                fim.value = "08:00"
                if operacao.value == "OBLL":
                    operacao.value = "Guarda"
            e.control.page.update()
        turno.on_change = on_turno_change

        # Funções dos botões
        def limpar_campos(e):
            if self.navigation_callback:
                self.navigation_callback(self.current_nav)

        def gravar_extra(e):
            # 1. Buscar policial_id
            policial_info = self.app.db.get_policial_by_matricula(matricula.value.strip())
            if not policial_info:
                show_alert_dialog(e.control.page, "Matrícula não encontrada!", success=False)
                return
            policial_id = policial_info.get("id")

            # 2. Buscar data_id na tabela calendario
            data_formatada = data.value.strip()
            if len(data_formatada) != 10:
                show_alert_dialog(e.control.page, "Data inválida!", success=False)
                return
            partes = data_formatada.split("/")
            data_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
            query_cal = "SELECT id FROM calendario WHERE data = ?"
            result_cal = self.app.db.execute_query(query_cal, (data_sql,))
            if not result_cal:
                show_alert_dialog(e.control.page, "Data não encontrada no calendário!", success=False)
                return
            data_id = result_cal[0]["id"]

            # 3. Verificações de exclusividade
            turno_val = turno.value
            operacao_val = operacao.value
            query_exist = "SELECT * FROM extras WHERE policial_id = ? AND data_id = ? AND turno = ? AND operacao = ?"
            exist = self.app.db.execute_query(query_exist, (policial_id, data_id, turno_val, operacao_val))
            if exist:
                show_alert_dialog(e.control.page, "Já existe uma extra com essa combinação!", success=False)
                return

            # Regra 2: Diurno/Noturno não pode coexistir com operação OBLL
            query_conflict_obll = "SELECT * FROM extras WHERE policial_id = ? AND data_id = ? AND operacao = 'OBLL'"
            conflict_obll = self.app.db.execute_query(query_conflict_obll, (policial_id, data_id))
            if turno_val in ["Diurno", "Noturno"] and conflict_obll:
                show_alert_dialog(e.control.page, "Já existe extra OBLL para esse policial e data!", success=False)
                return

            # Regra 3: OBLL não pode coexistir com turno Diurno/Noturno
            query_conflict_dn = "SELECT * FROM extras WHERE policial_id = ? AND data_id = ? AND turno IN ('Diurno', 'Noturno')"
            conflict_dn = self.app.db.execute_query(query_conflict_dn, (policial_id, data_id))
            if operacao_val == "OBLL" and conflict_dn:
                show_alert_dialog(e.control.page, "Já existe extra Diurno/Noturno para esse policial e data!", success=False)
                return

            # 4. Buscar intertício pelo nome usando a data informada
            interticio_nome = ""
            try:
                query_interticio = (
                    "SELECT nome FROM interticios "
                    "WHERE date(?) BETWEEN date(data_inicial) AND date(data_final) LIMIT 1"
                )
                result_interticio = self.app.db.execute_query(query_interticio, (data_sql,))
                if result_interticio and len(result_interticio) > 0:
                    if isinstance(result_interticio[0], dict) or hasattr(result_interticio[0], "keys"):
                        interticio_nome = result_interticio[0]["nome"]
                    else:
                        interticio_nome = result_interticio[0][0]
            except Exception as e:
                interticio_nome = ""

            # 5. NOVA VERIFICAÇÃO: Verificar limite de horas por intertício
            if interticio_nome:
                # Buscar todas as extras do policial no intertício
                query_horas_interticio = """
                    SELECT e.horas 
                    FROM extras e 
                    JOIN calendario c ON e.data_id = c.id 
                    JOIN interticios i ON date(c.data) BETWEEN date(i.data_inicial) AND date(i.data_final)
                    WHERE e.policial_id = ? AND i.nome = ?
                """
                result_horas = self.app.db.execute_query(query_horas_interticio, (policial_id, interticio_nome))
                
                # Calcular total de horas já cadastradas
                total_horas_existentes = 0
                if result_horas:
                    for row in result_horas:
                        horas_valor = row.get("horas") if isinstance(row, dict) else row[0]
                        try:
                            total_horas_existentes += int(horas_valor)
                        except (ValueError, TypeError):
                            pass
                
                # Adicionar as horas da nova extra
                horas_nova_extra = int(quant_horas.value) if quant_horas.value else 0
                total_final = total_horas_existentes + horas_nova_extra
                
                # Verificar se excede o limite de 96 horas
                if total_final > 96:
                    show_alert_dialog(
                        e.control.page, 
                        f"Limite de horas excedido para o intertício '{interticio_nome}'!\n"
                        f"Horas existentes: {total_horas_existentes}\n"
                        f"Horas da nova extra: {horas_nova_extra}\n"
                        f"Total: {total_final} (máximo: 96)", 
                        success=False
                    )
                    return

            # 6. Inserir extra incluindo o intertício
            command = """
                INSERT INTO extras (inicio, fim, horas, operacao, turno, policial_id, data_id, interticio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            horas_val = quant_horas.value
            inicio_val = inicio.value
            fim_val = fim.value
            print("[DEBUG] Dados para gravar na tabela extras:")
            print(f"inicio: {inicio_val}")
            print(f"fim: {fim_val}")
            print(f"horas: {horas_val}")
            print(f"operacao: {operacao_val}")
            print(f"turno: {turno_val}")
            print(f"policial_id: {policial_id}")
            print(f"data_id: {data_id}")
            print(f"interticio: {interticio_nome}")
            success = self.app.db.execute_command(command, (
                inicio_val, fim_val, horas_val, operacao_val, turno_val, policial_id, data_id, interticio_nome
            ))
            if success:
                show_alert_dialog(e.control.page, "Extra gravada com sucesso!", success=True)
            else:
                show_alert_dialog(e.control.page, "Erro ao gravar extra!", success=False)

        # Layout do formulário em duas colunas e quatro linhas
        # DatePicker
        import datetime
        datepicker = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )
        def on_date_change(e):
            if datepicker.value:
                data.value = datepicker.value.strftime("%d/%m/%Y")
                data.cursor_position = len(data.value)
                atualizar_interticio()
                e.control.page.update()
        datepicker.on_change = on_date_change

        def open_date_picker(e):
            page = e.control.page
            if datepicker not in page.overlay:
                page.overlay.append(datepicker)
                page.update()
            page.open(datepicker)

        btn_quant_horas = ft.ElevatedButton(
            text="Selecionar Data",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(
                    width=1,
                    color=ft.Colors.BLACK
                )
            ),
            width=matricula.width,
            height=matricula.height,
            on_click=open_date_picker
        )
        
        form_grid = ft.Column([
            ft.Row([
                matricula, policial
            ], spacing=40, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                btn_quant_horas, data
            ], spacing=40, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                turno, operacao
            ], spacing=40, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                inicio, fim
            ], spacing=40, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                c_interticio, c_horas_disp
            ], spacing=40, alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # Botões
        btn_gravar = ft.ElevatedButton(
            text="Gravar",
            width=150,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.GREEN,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.GREEN)),
            icon=ft.Icons.SAVE,
            on_click=gravar_extra,
        )
        btn_limpar = ft.ElevatedButton(
            text="Limpar",
            width=150,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.RED,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.RED)),
            icon=ft.Icons.DELETE,
            on_click=limpar_campos,
        )

        btn_row = ft.Row([
            btn_gravar,
            btn_limpar
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            ft.Text("Cadastrar Extra", size=28, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20),
            form_grid,
            ft.Container(height=30),
            btn_row
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
