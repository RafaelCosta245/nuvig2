import flet as ft
from .base_screen import BaseScreen
from dialogalert import show_alert_dialog

class CadastrarExtraScreen(BaseScreen):
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from dialogalert import show_alert_dialog
    from dialogalert import show_alert_dialog
    def get_content(self) -> ft.Control:
        # Campos do formulário
        matricula = ft.TextField(label="Matrícula", width=200, input_filter=ft.NumbersOnlyInputFilter())
        policial = ft.TextField(label="Policial", width=200, read_only=True)
        data = ft.TextField(label="Data", width=200, hint_text="dd/mm/aaaa")
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
            e.control.page.update()
        data.on_change = mascara_data
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "cadastrar_extra"

    def get_content(self) -> ft.Control:
        # Campos do formulário
        matricula = ft.TextField(label="Matrícula", width=200, input_filter=ft.NumbersOnlyInputFilter())
        policial = ft.TextField(label="Policial", width=200, read_only=True)
        data = ft.TextField(label="Data", width=200, hint_text="dd/mm/aaaa")
        operacao = ft.Dropdown(
            label="Operação",
            width=200,
            options=[
                ft.dropdown.Option("Guarda"),
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

        # Função para lógica do dropdown operação
        def on_operacao_change(e):
            if operacao.value == "OBLL":
                turno.value = "Vespertino"
                quant_horas.value = "12"
                inicio.value = "16:00"
                fim.value = "04:00"
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

            # 4. Inserir extra
            command = """
                INSERT INTO extras (inicio, fim, horas, operacao, turno, policial_id, data_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            horas_val = quant_horas.value
            inicio_val = inicio.value
            fim_val = fim.value
            success = self.app.db.execute_command(command, (
                inicio_val, fim_val, horas_val, operacao_val, turno_val, policial_id, data_id
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
    # Removido: Adiciona o datepicker ao overlay da página
        def on_date_change(e):
            if datepicker.value:
                data.value = datepicker.value.strftime("%d/%m/%Y")
                data.cursor_position = len(data.value)
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
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # Botões
        btn_gravar = ft.ElevatedButton(
            text="Gravar",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=gravar_extra,
            bgcolor=ft.Colors.BLUE,
            color=ft.Colors.WHITE
        )
        btn_limpar = ft.ElevatedButton(
            text="Limpar",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            on_click=limpar_campos,
            bgcolor=ft.Colors.GREY,
            color=ft.Colors.WHITE
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
