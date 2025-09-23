import flet as ft
from .base_screen import BaseScreen
import datetime


class CadastrarAusenciasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "cadastrar_ausencia"

    def get_content(self) -> ft.Control:
        # Buscar policial por matrícula (reutiliza a mesma lógica de férias)
        def buscar_policial(e):
            valor = matricula.value.strip()
            if valor:
                policial_info = self.app.db.get_policial_by_matricula(valor)
                if policial_info:
                    policial.value = policial_info.get("qra", "")
                    nome.value = policial_info.get("nome", "")
                    escala = policial_info.get("escala", "")
                    equipe.value = escala[0] if escala else ""
                else:
                    policial.value = ""
                    nome.value = ""
                    equipe.value = ""
            else:
                policial.value = ""
                nome.value = ""
                equipe.value = ""
            e.control.page.update()

        # Busca EXATA por QRA/Nome ao digitar no campo 'policial'
        def buscar_policial_por_qra_ou_nome(e):
            termo = policial.value.strip()
            if not termo:
                e.control.page.update()
                return
            try:
                query = (
                    """
                    SELECT id, nome, qra, matricula, escala
                    FROM policiais
                    WHERE unidade = 'NUVIG'
                      AND (
                            UPPER(qra) = UPPER(?)
                         OR UPPER(nome) = UPPER(?)
                          )
                    LIMIT 1
                    """
                )
                rows = self.app.db.execute_query(query, (termo, termo))
                if rows:
                    row = rows[0]
                    matricula.value = (row["matricula"] if "matricula" in row.keys() else matricula.value) or matricula.value
                    policial.value = (row["qra"] if "qra" in row.keys() else policial.value) or policial.value
                    nome.value = (row["nome"] if "nome" in row.keys() else nome.value) or nome.value
                    escala = row["escala"] if "escala" in row.keys() else ""
                    equipe.value = escala[0] if escala else equipe.value
            except Exception as err:
                print(f"[Ausências] Erro ao buscar por QRA/Nome: {err}")
            e.control.page.update()

        # Validadores simples
        def validar_ordem_datas(data_inicio, data_fim):
            if not data_inicio or not data_fim:
                return True
            try:
                inicio = datetime.datetime.strptime(data_inicio, "%d/%m/%Y")
                fim = datetime.datetime.strptime(data_fim, "%d/%m/%Y")
                return fim >= inicio
            except Exception:
                return False

        from dialogalert import show_alert_dialog
        def mostrar_erro_data(page, mensagem):
            show_alert_dialog(page, mensagem, success=False)

        # Campos
        matricula = ft.TextField(label="Matrícula", width=200, max_length=8, on_change=buscar_policial)
        policial = ft.TextField(label="QRA", width=200, read_only=False)
        nome = ft.TextField(label="Nome", width=200, read_only=True, disabled=True,
                             bgcolor=ft.Colors.GREY_100, border_color=ft.Colors.GREY_400,
                             text_style=ft.TextStyle(color=ft.Colors.GREY_700))
        equipe = ft.TextField(label="Equipe", width=200, read_only=True, disabled=True,
                               bgcolor=ft.Colors.GREY_100, border_color=ft.Colors.GREY_400,
                               text_style=ft.TextStyle(color=ft.Colors.GREY_700))

        licenca = ft.Dropdown(
            label="Motivo",
            width=(2*nome.width + 32),
            options=[
                ft.dropdown.Option("Licença para tratamento de saúde"),
                ft.dropdown.Option("Licença maternidade"),
                ft.dropdown.Option("Licença paternidade"),
                ft.dropdown.Option("Licença para acompanhar cônjuge"),
                ft.dropdown.Option("Licença por doença em familiar"),
                ft.dropdown.Option("Licença por acidente de trabalho"),
                ft.dropdown.Option("Licença para serviço militar"),
                ft.dropdown.Option("Licença em caráter especial"),
                ft.dropdown.Option("Curso operacional SAP/CE"),
                ft.dropdown.Option("Curso de formação profissional"),
                ft.dropdown.Option("Outro"),
            ]
        )

        dias = ft.Text(size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER)

        data_inicio1 = ft.TextField(label="Data Início", width=200, hint_text="dd/mm/aaaa")
        data_fim1 = ft.TextField(label="Data Fim", width=200, hint_text="dd/mm/aaaa")

        # Máscaras
        def mask_date(field):
            valor = ''.join(c for c in field.value if c.isdigit())
            novo = ''
            if len(valor) > 0:
                novo += valor[:2]
            if len(valor) > 2:
                novo += '/' + valor[2:4]
            if len(valor) > 4:
                novo += '/' + valor[4:8]
            field.value = novo

        def _parse_ddmmyyyy_or_iso(s: str) -> datetime.datetime | None:
            try:
                if not s:
                    return None
                if '-' in s and len(s) >= 10:
                    # ISO yyyy-mm-dd
                    ano, mes, dia = s[:10].split('-')
                    return datetime.datetime(int(ano), int(mes), int(dia))
                if '/' in s and len(s) >= 10:
                    dia, mes, ano = s[:10].split('/')
                    return datetime.datetime(int(ano), int(mes), int(dia))
                return None
            except Exception:
                return None

        def atualizar_qtd_dias():
            try:
                d1 = _parse_ddmmyyyy_or_iso(data_inicio1.value)
                d2 = _parse_ddmmyyyy_or_iso(data_fim1.value)
                if d1 and d2:
                    qnt = (d2 - d1).days + 1
                    if qnt > 0:
                        dias.value = f"{qnt} dias"
                    else:
                        dias.value = ""
                else:
                    dias.value = ""
            except Exception:
                dias.value = ""

        def on_change_inicio(e):
            mask_date(data_inicio1)
            atualizar_qtd_dias()
            e.control.page.update()

        def on_change_fim(e):
            mask_date(data_fim1)
            atualizar_qtd_dias()
            e.control.page.update()

        data_inicio1.on_change = on_change_inicio
        data_fim1.on_change = on_change_fim

        # Ativar busca exata por QRA/Nome ao digitar no campo 'policial'
        policial.on_change = buscar_policial_por_qra_ou_nome

        # DatePickers (apenas período 1)
        datepicker_inicio1 = ft.DatePicker(first_date=datetime.datetime(2020, 1, 1), last_date=datetime.datetime(2030, 12, 31))
        datepicker_fim1 = ft.DatePicker(first_date=datetime.datetime(2020, 1, 1), last_date=datetime.datetime(2030, 12, 31))

        def on_inicio1_change(e):
            if datepicker_inicio1.value:
                data_inicio1.value = datepicker_inicio1.value.strftime("%d/%m/%Y")
                if not validar_ordem_datas(data_inicio1.value, data_fim1.value):
                    data_inicio1.value = ""
                atualizar_qtd_dias()
                e.control.page.update()

        def on_fim1_change(e):
            if datepicker_fim1.value:
                data_fim1.value = datepicker_fim1.value.strftime("%d/%m/%Y")
                if not validar_ordem_datas(data_inicio1.value, data_fim1.value):
                    data_fim1.value = ""
                atualizar_qtd_dias()
                e.control.page.update()

        datepicker_inicio1.on_change = on_inicio1_change
        datepicker_fim1.on_change = on_fim1_change

        def open_picker(picker, page):
            if picker not in page.overlay:
                page.overlay.append(picker)
                page.update()
            page.open(picker)

        btn_inicio1 = ft.ElevatedButton(
            text="Início",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), side=ft.BorderSide(width=1, color=ft.Colors.BLACK)),
            width=100,
            on_click=lambda e: open_picker(datepicker_inicio1, e.control.page)
        )
        btn_fim1 = ft.ElevatedButton(
            text="Fim",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), side=ft.BorderSide(width=1, color=ft.Colors.BLACK)),
            width=100,
            on_click=lambda e: open_picker(datepicker_fim1, e.control.page)
        )

        # Botões principais (sem persistência por enquanto)
        def limpar(e):
            if self.navigation_callback:
                self.navigate_to(self.current_nav)  # Tenta recarregar a tela via navegação
            # matricula.value = policial.value = nome.value = equipe.value = ""
            # data_inicio1.value = data_fim1.value = ""
            # dias.value = ""
            # licenca.value = None
            # licenca.update()
            # e.control.page.update()

        def gravar(e):
            try:
                if not matricula.value.strip():
                    mostrar_erro_data(e.control.page, "Matrícula é obrigatória!")
                    return
                if not data_inicio1.value.strip() or not data_fim1.value.strip():
                    mostrar_erro_data(e.control.page, "Informe início e fim da ausência.")
                    return
                if not validar_ordem_datas(data_inicio1.value, data_fim1.value):
                    mostrar_erro_data(e.control.page, "Data fim deve ser igual ou posterior à data início.")
                    return

                # Buscar policial por matrícula
                policial_info = self.app.db.get_policial_by_matricula(matricula.value.strip())
                if not policial_info:
                    show_alert_dialog(e.control.page, "Policial não encontrado pela matrícula!", success=False)
                    return
                policial_id = policial_info.get("id")

                # Converter datas dd/mm/aaaa -> yyyy-mm-dd
                def conv(d):
                    dt = _parse_ddmmyyyy_or_iso(d)
                    return dt.strftime("%Y-%m-%d") if dt else ""

                inicio_sql = conv(data_inicio1.value.strip())
                fim_sql = conv(data_fim1.value.strip())
                licenca_val = licenca.value or ""
                # calcular quantidade de dias (inclusivo)
                d1 = _parse_ddmmyyyy_or_iso(data_inicio1.value.strip())
                d2 = _parse_ddmmyyyy_or_iso(data_fim1.value.strip())
                qnt = (d2 - d1).days + 1 if d1 and d2 else 0
                if qnt <= 0:
                    show_alert_dialog(e.control.page, "Período inválido (quantidade de dias <= 0)", success=False)
                    return
                # refletir na UI
                dias.value = f"{qnt} dias"
                try:
                    dias.update()
                except Exception:
                    pass

                # Inserir em licencas(id, policial_id, licenca, inicio, fim)
                cmd = """
                    INSERT INTO licencas (policial_id, licenca, inicio, fim, qty_dias)
                    VALUES (?, ?, ?, ?, ?)
                """
                ok = self.app.db.execute_command(cmd, (policial_id, licenca_val, inicio_sql, fim_sql, qnt))
                if ok:
                    show_alert_dialog(e.control.page, "Ausência registrada com sucesso!", success=True)
                    limpar(e)
                else:
                    show_alert_dialog(e.control.page, "Erro ao registrar ausência!", success=False)
            except Exception as ex:
                show_alert_dialog(e.control.page, f"Erro inesperado: {ex}", success=False)

        btn_gravar = ft.ElevatedButton(text="Registrar",
                                       bgcolor=ft.Colors.WHITE,
                                       color=ft.Colors.GREEN,
                                       width=120,
                                       style=ft.ButtonStyle(
                                           color=ft.Colors.BLACK,
                                           text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                                           shape=ft.RoundedRectangleBorder(radius=8),
                                           side=ft.BorderSide(1, ft.Colors.GREEN)),
                                       icon=ft.Icons.SAVE,
                                       on_click=gravar)
        btn_limpar = ft.ElevatedButton(text="Limpar",
                                       bgcolor=ft.Colors.WHITE,
                                       color=ft.Colors.RED,
                                       width=btn_gravar.width,
                                       style=ft.ButtonStyle(
                                           color=ft.Colors.BLACK,
                                           text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                                           shape=ft.RoundedRectangleBorder(radius=8),
                                           side=ft.BorderSide(1, ft.Colors.RED)),
                                       icon=ft.Icons.DELETE,
                                       on_click=limpar)

        form = ft.Column([
            ft.Text("Registro de Ausências", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
            ft.Container(height=10),
            ft.Row([matricula, policial], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([nome, equipe], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            licenca,
            ft.Container(height=10),
            ft.Text("Período", size=16, weight=ft.FontWeight.BOLD),
            ft.Row([btn_inicio1, data_inicio1, btn_fim1, data_fim1], spacing=16, alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            dias,
            ft.Container(height=20),
            ft.Row([btn_gravar, btn_limpar], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        #return ft.Column([form], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        return form
