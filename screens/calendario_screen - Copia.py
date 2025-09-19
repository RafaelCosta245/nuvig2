import flet as ft
from .base_screen import BaseScreen
import calendar
from datetime import date

class CalendarioScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "calendario"
        
        hoje = date.today()
        self.displayed_year = hoje.year
        self.displayed_month = hoje.month
        self.month_title_text: ft.Text | None = None
        self.calendar_container: ft.Container | None = None
        
    def get_content(self) -> ft.Control:
        # Calendário interativo (substitui o formulário)
        self.calendar_container = ft.Container(
            content=self._build_calendar_controls(),
            padding=ft.padding.all(20),
            border=ft.border.all(1, ft.Colors.GREY),
            border_radius=15,
            bgcolor=ft.Colors.WHITE,
            width=500
        )

        self.escala_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Escala do dia", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=15),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO
            ),
            padding=ft.padding.all(20),
            border=ft.border.all(1, ft.Colors.GREY),
            border_radius=15,
            bgcolor=ft.Colors.WHITE,
            width=800,
            height=500
        )

        segunda_coluna = self.escala_container

        # Alinha o topo do calendário com o topo da tabela de escalas
        content = ft.Stack(
            controls=[
                ft.Container(content=self.calendar_container, top=100, left=20),
                ft.Container(content=segunda_coluna, top=100, left=560)
            ],
            width=1400,
            height=800
        )

        return content
        
    # --- Calendário ---
    def _month_title(self) -> str:
        nome_mes = calendar.month_name[self.displayed_month]
        return f"{nome_mes} {self.displayed_year}"

    def _build_calendar_controls(self) -> ft.Control:
        calendar.setfirstweekday(calendar.SUNDAY)
        matriz = calendar.monthcalendar(self.displayed_year, self.displayed_month)

        # Cabeçalho com navegação do calendário (mês/ano)
        self.month_title_text = ft.Text(self._month_title(), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=self.prev_month, tooltip="Mês anterior"),
                    self.month_title_text,
                    ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=self.next_month, tooltip="Próximo mês"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            alignment=ft.alignment.center,
            width=500,
            padding=ft.padding.only(top=0, bottom=10)
        )

        dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        header_days = ft.Row(
            controls=[ft.Text(d, width=60, size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER) for d in dias],
            spacing=5,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        linhas = []
        for semana in matriz:
            cells = []
            for dia in semana:
                if dia == 0:
                    cells.append(ft.Container(width=60, height=40))
                else:
                    cells.append(
                        ft.TextButton(
                            text=str(dia),
                            width=60,
                            height=40,
                            on_click=lambda e, d=dia: self.on_day_click(d)
                        )
                    )
            linhas.append(ft.Row(controls=cells, spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))

        return ft.Column(controls=[header, header_days] + linhas, spacing=8)

    def prev_month(self, e):
        if self.displayed_month == 1:
            self.displayed_month = 12
            self.displayed_year -= 1
        else:
            self.displayed_month -= 1
        if self.month_title_text:
            self.month_title_text.value = self._month_title()
            self.month_title_text.update()
        if self.calendar_container:
            self.calendar_container.content = self._build_calendar_controls()
            self.calendar_container.update()

    def next_month(self, e):
        if self.displayed_month == 12:
            self.displayed_month = 1
            self.displayed_year += 1
        else:
            self.displayed_month += 1
        if self.month_title_text:
            self.month_title_text.value = self._month_title()
            self.month_title_text.update()
        if self.calendar_container:
            self.calendar_container.content = self._build_calendar_controls()
            self.calendar_container.update()

    def on_day_click(self, dia: int):
        from datetime import datetime, timedelta
        data_str = f"{self.displayed_year:04d}-{self.displayed_month:02d}-{dia:02d}"
        equipe = self.app.db.get_equipe_by_data(data_str)
        policiais = self.app.db.execute_query("SELECT qra, escala, inicio, nome, situacao FROM policiais")
        escalados = []
        licencas = []
        if equipe:
            for policial in policiais:
                escala = policial["escala"]
                inicio = policial["inicio"]
                qra = policial["qra"]
                situacao = policial["situacao"] if "situacao" in policial.keys() else ""
                if not escala or not inicio:
                    continue
                ciclo_letras = list(escala)
                ciclo_len = len(ciclo_letras) * 4 if len(ciclo_letras) > 1 else 4
                try:
                    inicio_dt = datetime.strptime(inicio, "%Y-%m-%d")
                    dia_dt = datetime.strptime(data_str, "%Y-%m-%d")
                except Exception:
                    continue
                dias_passados = (dia_dt - inicio_dt).days
                if dias_passados < 0:
                    continue
                ciclo_pos = dias_passados % ciclo_len
                escalado_hoje = False
                if len(ciclo_letras) > 1:
                    if ciclo_pos < len(ciclo_letras):
                        letra_do_dia = ciclo_letras[ciclo_pos]
                        if letra_do_dia == equipe:
                            escalado_hoje = True
                else:
                    if ciclo_pos == 0 and escala == equipe:
                        escalado_hoje = True
                if escalado_hoje:
                    if situacao.lower() == "inativo":
                        licencas.append(f"{qra} (LTS)")
                    else:
                        escalados.append(qra)
            # Distribuição dos QRA nas colunas
            import random
            random.shuffle(escalados)
            acesso_01 = escalados[:4]
            acesso_03 = escalados[4:6]
            acesso_02 = escalados[6:]
            obll = []
            # Título com data e equipe
            data_formatada = f"{dia:02d}/{self.displayed_month:02d}/{self.displayed_year}"
            titulo = f"Escala do dia ({data_formatada}) - Equipe {equipe}"
            col_width = 130
            titulos_row = ft.Row([
                ft.Text("Acesso 01", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE, width=col_width, text_align=ft.TextAlign.CENTER),
                ft.Text("Acesso 02", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE, width=col_width, text_align=ft.TextAlign.CENTER),
                ft.Text("Acesso 03", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE, width=col_width, text_align=ft.TextAlign.CENTER),
                ft.Text("OBLL", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE, width=col_width, text_align=ft.TextAlign.CENTER),
                ft.Text("Licenças", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE, width=col_width, text_align=ft.TextAlign.CENTER)
            ], spacing=5, alignment=ft.MainAxisAlignment.CENTER)

            max_linhas = max(len(acesso_01), len(acesso_02), len(acesso_03), len(licencas), 1)
            linhas_grid = []
            for i in range(max_linhas):
                row = ft.Row([
                    ft.Text(acesso_01[i] if i < len(acesso_01) else "", size=16, color=ft.Colors.BLACK, width=col_width, text_align=ft.TextAlign.CENTER),
                    ft.Text(acesso_02[i] if i < len(acesso_02) else "", size=16, color=ft.Colors.BLACK, width=col_width, text_align=ft.TextAlign.CENTER),
                    ft.Text(acesso_03[i] if i < len(acesso_03) else "", size=16, color=ft.Colors.BLACK, width=col_width, text_align=ft.TextAlign.CENTER),
                    ft.Text("", size=16, color=ft.Colors.BLACK, width=col_width, text_align=ft.TextAlign.CENTER),
                    ft.Text(licencas[i] if i < len(licencas) else "", size=16, color=ft.Colors.BLACK, width=col_width, text_align=ft.TextAlign.CENTER)
                ], spacing=5, alignment=ft.MainAxisAlignment.CENTER)
                linhas_grid.append(row)

            grid = ft.Column([
                titulos_row,
                *linhas_grid
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

            escala_texts = [ft.Text(titulo, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE, text_align=ft.TextAlign.CENTER), ft.Container(height=15), grid]
            if not escalados and not licencas:
                escala_texts.append(ft.Text("Nenhum policial escalado", size=16, color=ft.Colors.RED))
            self.escala_container.content = ft.Column(escala_texts, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.escala_container.update()
        else:
            print("[DEBUG] Nenhuma equipe cadastrada para esta data")
            escala_texts = [ft.Text("Nenhuma equipe cadastrada para esta data", size=16, color=ft.Colors.RED)]
            self.escala_container.content = ft.Column(escala_texts, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            self.escala_container.update()
        print(f"[DEBUG] on_day_click finalizado para dia {dia}")
            
    def criar_tabela_acessos(self) -> ft.Control:
        acessos = self.app.db.buscar_acessos_sem_saida()
        if not acessos:
            return ft.Container(content=ft.Text("Nenhum acesso ativo encontrado", color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER), padding=ft.padding.all(20), alignment=ft.alignment.center)
        headers = ["Nome", "Documento", "Veículo", "Placa", "Destino", "Entrada"]
        rows = []
        for acesso in acessos:
            row = ft.Row(controls=[
                ft.Text(acesso.get('nome', ''), size=12, width=120, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(acesso.get('documento', ''), size=12, width=100, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(acesso.get('veiculo', ''), size=12, width=120, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(acesso.get('placa', ''), size=12, width=80, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(acesso.get('destino', ''), size=12, width=150, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(acesso.get('entrada', ''), size=12, width=120, overflow=ft.TextOverflow.ELLIPSIS)
            ], spacing=15)
            rows.append(row)
        header_row = ft.Row(controls=[
            ft.Text(headers[0], size=12, weight=ft.FontWeight.BOLD, width=120, color=ft.Colors.BLUE),
            ft.Text(headers[1], size=12, weight=ft.FontWeight.BOLD, width=100, color=ft.Colors.BLUE),
            ft.Text(headers[2], size=12, weight=ft.FontWeight.BOLD, width=120, color=ft.Colors.BLUE),
            ft.Text(headers[3], size=12, weight=ft.FontWeight.BOLD, width=80, color=ft.Colors.BLUE),
            ft.Text(headers[4], size=12, weight=ft.FontWeight.BOLD, width=150, color=ft.Colors.BLUE),
            ft.Text(headers[5], size=12, weight=ft.FontWeight.BOLD, width=120, color=ft.Colors.BLUE)
        ], spacing=15)
        tabela_container = ft.Container(content=ft.Column(controls=[header_row, ft.Divider(height=1)] + rows, spacing=5, scroll=ft.ScrollMode.AUTO), width=750, height=400, padding=ft.padding.all(10))
        return tabela_container


