import flet as ft
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Image, SimpleDocTemplate, Spacer
from reportlab.lib.units import cm
from reportlab.lib.units import inch
import os
from database.database_manager import DatabaseManager
import datetime
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import traceback

class DisponibilidadeFeriasScreen:
    def __init__(self, app):
        self.app = app
        self.selected_opcao = "A"
        self.selected_ano = "2025"
        self.tabela_column = None

    def get_content(self):


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
                print("[Disponibilidade][EXCEPTION]", ex)
                print(traceback.format_exc())
                self.tabela_column.controls = [ft.Text(f"Erro ao atualizar tabela: {ex}", size=16, color=ft.Colors.RED)]
                safe_update()

        def gerar_relatorio(e=None):
            try:

                escala_letra = dropdown_opcao.value
                ano = int(dropdown_ano.value)

                # Reaproveitar a construção das linhas atuais convertendo para uma lista simples
                if not isinstance(self.tabela_column.controls, list) or not self.tabela_column.controls:
                    print("[Relatorio] Sem dados para gerar o relatório.")
                    return

                # Extrair linhas da DataTable
                data_rows = [["Mês/Ano", "Equipe", "Início", "Fim", "Quant. Dias"]]
                if isinstance(self.tabela_column.controls[0], ft.DataTable):
                    dt = self.tabela_column.controls[0]
                    for r in dt.rows:
                        valores = []
                        for c in r.cells:
                            # c.content é um ft.Text
                            if hasattr(c.content, "value"):
                                valores.append(str(c.content.value))
                            else:
                                valores.append("")
                        data_rows.append(valores)
                else:
                    # Se não for DataTable, há mensagem de vazio
                    print("[Relatorio] Tabela vazia ou em formato inesperado.")
                    return

                # Caminho do PDF (prioriza roots.save_path; fallback: self.app.output_dir; por fim: cwd)
                try:
                    db_mgr = self.app.db if hasattr(self.app, 'db') else DatabaseManager()
                except Exception:
                    db_mgr = DatabaseManager()
                base_dir = db_mgr.get_root_path("save_path")
                if not base_dir or not os.path.isdir(base_dir):
                    base_dir = getattr(self.app, "output_dir", None) if hasattr(self, 'app') else None
                if not base_dir or not os.path.isdir(base_dir):
                    base_dir = os.getcwd()
                pdf_filename = f"disponibilidade_ferias_{escala_letra}_{ano}.pdf"
                pdf_path = os.path.join(base_dir, pdf_filename)
                print(f"[Relatorio] Gerando PDF: {pdf_path}")
                # Garante que diretório exista
                try:
                    os.makedirs(base_dir, exist_ok=True)
                except Exception as _mk:
                    print(f"[Relatorio] Aviso: não foi possível criar diretório '{base_dir}': {_mk}")

                doc = SimpleDocTemplate(
                    pdf_path,
                    pagesize=A4,
                    rightMargin=1.5*cm,
                    leftMargin=1.5*cm,
                    topMargin=1.5*cm,
                    bottomMargin=1.5*cm,
                )

                elements = []

                # Cabeçalho com logo
                logo_path = os.path.abspath("assets/icons/logoNUVIG.png")
                if os.path.exists(logo_path):
                    img = Image(logo_path, width=4*cm, height=3*cm)
                    img.hAlign = 'CENTER'
                    elements.append(img)
                else:
                    print(f"[Relatorio] Logo não encontrada em {logo_path}")

                elements.append(Spacer(1, 0.5*cm))

                # Título
                styles = getSampleStyleSheet()
                titulo = Paragraph(f"Disponibilidade de Férias — Equipe {escala_letra} — {ano}", styles['Title'])
                elements.append(titulo)
                elements.append(Spacer(1, 0.5*cm))

                # Tabela
                t = Table(data_rows, hAlign='CENTER')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 10),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ]))
                elements.append(t)

                doc.build(elements)
                print(f"[Relatorio] PDF gerado com sucesso: {pdf_path}")
            except Exception as ex:

                print("[Relatorio][EXCEPTION]", ex)
                print(traceback.format_exc())

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
            label="Equipe",
            filled=True,  # Precisa ser True para fill_color funcionar
            fill_color=ft.Colors.WHITE,
            on_change=atualizar_tabela
        )
        dropdown_ano = ft.Dropdown(
            options=[
                ft.dropdown.Option(str(ano)) for ano in range(2025, 2031)
            ],
            value=self.selected_ano,
            width=120,
            label="Ano",
            filled=True,  # Precisa ser True para fill_color funcionar
            fill_color=ft.Colors.WHITE,
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
            height=450,
            border_radius=10,
            padding=20,
            alignment=ft.alignment.top_center,
            #bgcolor=ft.Colors.ORANGE
        )

        # Column principal centralizada
        main_column = ft.Column(
            controls=[
                titulo,
                row_dropdowns,
                tabela_container,
                ft.Container(height=12),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            text="Gerar relatório",
                            icon=ft.Icons.PICTURE_AS_PDF,
                            color=ft.Colors.BLACK,
                            bgcolor=ft.Colors.WHITE,
                            width=150,
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLACK,
                                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                side=ft.BorderSide(1, ft.Colors.BLACK)),
                            on_click=gerar_relatorio
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            expand=True,
        )

        # Atualiza tabela ao abrir tela
        atualizar_tabela()
        return main_column

    def set_navigation_callback(self, callback):
        self.navigate_to = callback
