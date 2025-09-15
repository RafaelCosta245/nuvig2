import flet as ft

class DisponibilidadeFeriasScreen:
    def __init__(self, app):
        self.app = app
        self.selected_opcao = "A"
        self.selected_ano = "2025"
        self.tabela_column = None

    def get_content(self):
        from database.database_manager import DatabaseManager
        import datetime

        db = self.app.db if hasattr(self.app, "db") else DatabaseManager()

        def atualizar_tabela(e=None):
            try:
                def safe_update():
                    try:
                        if getattr(self.tabela_column, "page", None) is not None:
                            self.tabela_column.update()
                    except Exception as _ex:
                        # Evita erro "Control must be added to the page first" no carregamento inicial
                        pass
                escala_letra = dropdown_opcao.value
                ano = int(dropdown_ano.value)
                print("[Disponibilidade] Filtro selecionado:", {"equipe": escala_letra, "ano": ano})
                # Buscar policiais cuja escala começa com a letra selecionada
                query_pol = "SELECT id, nome, escala FROM policiais WHERE escala LIKE ?"
                param = escala_letra + "%"
                policiais = db.execute_query(query_pol, (param,))
                print(f"[Disponibilidade] Policiais encontrados (LIKE {param}): {len(policiais)}")
                if db.last_error:
                    print("[Disponibilidade][ERRO] Consulta policiais:", db.last_error)
                policial_ids = [p["id"] for p in policiais]
                print("[Disponibilidade] IDs dos policiais:", policial_ids)

                # Buscar férias desses policiais para o ano selecionado
                if not policial_ids:
                    self.tabela_column.controls = [ft.Text("Nenhum policial encontrado para a equipe selecionada.", size=16)]
                    safe_update()
                    return

                placeholders = ",".join(["?" for _ in policial_ids])
                query_ferias = f"SELECT policial_id, inicio1, fim1, inicio2, fim2, inicio3, fim3 FROM ferias WHERE policial_id IN ({placeholders})"
                ferias = db.execute_query(query_ferias, tuple(policial_ids))
                print(f"[Disponibilidade] Registros de férias retornados: {len(ferias)} para policiais: {policial_ids}")
                if db.last_error:
                    print("[Disponibilidade][ERRO] Consulta férias:", db.last_error)

                # Período total do ano
                year_start = datetime.datetime(ano, 1, 1)
                year_end = datetime.datetime(ano, 12, 31)
                print(f"[Disponibilidade] Intervalo do ano: {year_start:%d/%m/%Y} - {year_end:%d/%m/%Y}")

                # Coletar e normalizar intervalos de férias (clamp ao ano, ignorar fora do ano)
                busy_intervals = []
                for f in ferias:
                    for i in range(1, 3 + 1):
                        inicio = f[f"inicio{i}"]
                        fim = f[f"fim{i}"]
                        if not inicio or not fim:
                            continue
                        try:
                            dt_inicio = datetime.datetime.strptime(inicio, "%Y-%m-%d")
                            dt_fim = datetime.datetime.strptime(fim, "%Y-%m-%d")
                        except Exception:
                            print(f"[Disponibilidade] Ignorar férias inválidas policial_id={f['policial_id']} i={i} -> {inicio} a {fim}")
                            continue
                        # Normalizar ordem, caso venha invertida
                        if dt_fim < dt_inicio:
                            dt_inicio, dt_fim = dt_fim, dt_inicio
                        # Descartar se totalmente fora do ano
                        if dt_fim < year_start or dt_inicio > year_end:
                            continue
                        # Aparar aos limites do ano
                        start = max(dt_inicio, year_start)
                        end = min(dt_fim, year_end)
                        busy_intervals.append((start, end))

                print(f"[Disponibilidade] Intervalos de férias coletados (não mesclados): {len(busy_intervals)}")

                # Unificar intervalos sobrepostos ou contíguos
                busy_intervals.sort(key=lambda x: x[0])
                merged = []
                for interval in busy_intervals:
                    if not merged:
                        merged.append(list(interval))
                    else:
                        last_start, last_end = merged[-1]
                        cur_start, cur_end = interval
                        if cur_start <= last_end + datetime.timedelta(days=1):
                            merged[-1][1] = max(last_end, cur_end)
                        else:
                            merged.append([cur_start, cur_end])
                merged = [(s, e) for s, e in merged]
                print(f"[Disponibilidade] Intervalos de férias mesclados: {len(merged)} -> {[(a.strftime('%d/%m/%Y'), b.strftime('%d/%m/%Y')) for a,b in merged]}")

                # Calcular intervalos livres (complemento dentro do ano)
                free_intervals = []
                cursor = year_start
                for start, end in merged:
                    if start > cursor:
                        free_intervals.append((cursor, start - datetime.timedelta(days=1)))
                    cursor = max(cursor, end + datetime.timedelta(days=1))
                if cursor <= year_end:
                    free_intervals.append((cursor, year_end))

                # Filtrar por mínimo de 10 dias
                free_intervals_10 = []
                for fs, fe in free_intervals:
                    dias = (fe - fs).days + 1
                    if dias >= 10:
                        free_intervals_10.append((fs, fe, dias))
                    else:
                        print(f"[Disponibilidade] Descartar livre {fs:%d/%m/%Y}-{fe:%d/%m/%Y} dias={dias} (<10)")

                print(f"[Disponibilidade] Intervalos livres >=10 dias: {len(free_intervals_10)}")

                # Montar linhas para exibição
                linhas = []
                for fs, fe, dias in free_intervals_10:
                    linhas.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(f"{fs.month:02d}/{fs.year}")),
                        ft.DataCell(ft.Text(escala_letra)),
                        ft.DataCell(ft.Text(fs.strftime("%d/%m/%Y"))),
                        ft.DataCell(ft.Text(fe.strftime("%d/%m/%Y"))),
                        ft.DataCell(ft.Text(str(dias))),
                    ]))

                if not linhas:
                    print("[Disponibilidade] Nenhum intervalo livre suficiente para exibir.")
                    self.tabela_column.controls = [ft.Text("Nenhum período disponível para o filtro selecionado.", size=16)]
                else:
                    print(f"[Disponibilidade] Total de linhas a exibir: {len(linhas)}")
                    self.tabela_column.controls = [
                        ft.DataTable(
                            columns=[
                                ft.DataColumn(ft.Text("Mês/Ano")),
                                ft.DataColumn(ft.Text("Equipe")),
                                ft.DataColumn(ft.Text("Início")),
                                ft.DataColumn(ft.Text("Fim")),
                                ft.DataColumn(ft.Text("Quant. Dias")),
                            ],
                            rows=linhas,
                            show_checkbox_column=False
                        )
                    ]
                safe_update()
            except Exception as ex:
                import traceback
                print("[Disponibilidade][EXCEPTION]", ex)
                print(traceback.format_exc())
                self.tabela_column.controls = [ft.Text(f"Erro ao atualizar tabela: {ex}", size=16, color=ft.Colors.RED)]
                safe_update()

        # Título
        titulo = ft.Text(
            "Consulte a disponibilidade para férias",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        # Dropdowns
        dropdown_opcao = ft.Dropdown(
            options=[
                ft.dropdown.Option("A"),
                ft.dropdown.Option("B"),
                ft.dropdown.Option("C"),
                ft.dropdown.Option("D"),
            ],
            value=self.selected_opcao,
            width=120,
            on_change=atualizar_tabela
        )
        dropdown_ano = ft.Dropdown(
            options=[
                ft.dropdown.Option(str(ano)) for ano in range(2025, 2031)
            ],
            value=self.selected_ano,
            width=120,
            on_change=atualizar_tabela
        )
        row_dropdowns = ft.Row(
            controls=[dropdown_opcao, dropdown_ano],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30,
        )

        # Espaço para tabela com rolagem
        self.tabela_column = ft.Column(
            controls=[ft.Text("Tabela de disponibilidade será exibida aqui.", size=16)],
            spacing=10,
        )
        tabela_container = ft.Container(
            content=ft.ListView(
                controls=[self.tabela_column],
                expand=True,
                auto_scroll=False,
            ),
            width=600,
            height=550,
            border_radius=10,
            padding=20,
            alignment=ft.alignment.top_center,
        )

        # Column principal centralizada
        main_column = ft.Column(
            controls=[
                titulo,
                row_dropdowns,
                tabela_container,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )

        # Atualiza tabela ao abrir tela
        atualizar_tabela()
        return main_column

    def set_navigation_callback(self, callback):
        self.navigate_to = callback
