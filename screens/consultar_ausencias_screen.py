import flet as ft
from .base_screen import BaseScreen
from reportlab.lib.pagesizes import A4, landscape
import datetime
import json
import os
from dialogalert import show_alert_dialog
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ConsultarAusenciasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "consultar_ausencias"

    def get_content(self) -> ft.Control:

        # Título e filtro (apenas matrícula)
        titulo = ft.Text(
            "Consultar Ausências por Matrícula",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLACK,
            text_align=ft.TextAlign.CENTER,
        )
        field_policial = ft.TextField(label="Matrícula", width=200)
        filtros_row = ft.Row([field_policial], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

        # Controle para seleção única e cor de linha
        self.selected_row_index = None
        self.tabela_rows = []  # Guardar referências das linhas
        self.result_licencas = []  # Guardar os dados das licenças para referência
        
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

        # Tabela resultado
        tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nome", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("QRA", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Licença", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Início", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Fim", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Dias", text_align=ft.TextAlign.CENTER)),
                ft.DataColumn(ft.Text("Retorno", text_align=ft.TextAlign.CENTER)),
            ],
            rows=[],
            show_checkbox_column=False,
            column_spacing=20,
            data_row_min_height=50,
            heading_row_height=60,
            #border=ft.border.all(2, ft.Colors.GREY_400),
            border_radius=10,
        )
        tabela_container = ft.Container(
            content=ft.ListView(controls=[tabela], expand=True, padding=0, spacing=0),
            padding=10,
            expand=True,
            width=1000,
            #bgcolor=ft.Colors.WHITE,
            border_radius=10,
            alignment=ft.alignment.center
        )

        def _format_date(sql_date: str) -> str:
            try:
                if not sql_date:
                    return ""
                y, m, d = sql_date.split("-")
                return f"{d}/{m}/{y}"
            except Exception:
                return sql_date or ""

        def atualizar_tabela(_=None):
            matricula = field_policial.value.strip()
            tabela.rows.clear()
            self.tabela_rows.clear()
            if not matricula:
                tabela.update()
                return

            # Buscar policial
            db = self.app.db
            self.res_pol = db.execute_query("SELECT id, nome, qra FROM policiais WHERE matricula = ?", (matricula,))
            if not self.res_pol:
                tabela.update()
                return
            pol = self.res_pol[0]
            pid = pol["id"] if hasattr(pol, "keys") else pol[0]
            nome = pol["nome"] if hasattr(pol, "keys") else pol[1]
            qra = pol["qra"] if hasattr(pol, "keys") else pol[2]

            # Buscar licenças para o policial
            lics = db.execute_query(
                "SELECT licenca, inicio, fim, qty_dias FROM licencas WHERE policial_id = ? ORDER BY inicio DESC",
                (pid,),
            )
            
            # Armazenar os resultados para referência
            self.result_licencas = lics

            for idx, r in enumerate(lics):
                licenca = r["licenca"] if hasattr(r, "keys") else r[0]
                inicio = r["inicio"] if hasattr(r, "keys") else r[1]
                fim = r["fim"] if hasattr(r, "keys") else r[2]
                dias = r["qty_dias"] if hasattr(r, "keys") else r[3]
                try:
                    retorno = (
                        datetime.datetime.strptime(fim, "%Y-%m-%d") + datetime.timedelta(days=1)
                    ).strftime("%d/%m/%Y")
                except Exception:
                    retorno = ""
                
                dr = ft.DataRow(
                    selected=(self.selected_row_index == idx),
                    on_select_changed=on_row_select,
                    color=ft.Colors.GREY_200 if self.selected_row_index == idx else None,
                    cells=[
                        ft.DataCell(ft.Text(nome, text_align=ft.TextAlign.CENTER)),
                        ft.DataCell(ft.Text(qra or "", text_align=ft.TextAlign.CENTER)),
                        ft.DataCell(ft.Text(licenca or "", text_align=ft.TextAlign.CENTER)),
                        ft.DataCell(ft.Text(_format_date(inicio), text_align=ft.TextAlign.CENTER)),
                        ft.DataCell(ft.Text(_format_date(fim), text_align=ft.TextAlign.CENTER)),
                        ft.DataCell(ft.Text(str(dias) if dias is not None else "", text_align=ft.TextAlign.CENTER)),
                        ft.DataCell(ft.Text(retorno, text_align=ft.TextAlign.CENTER)),
                    ]
                )
                tabela.rows.append(dr)
                self.tabela_rows.append(dr)
            tabela.update()

        field_policial.on_change = atualizar_tabela

        # Função para apagar a licença selecionada
        def apagar_licenca(e):
            if self.selected_row_index is None:
                show_alert_dialog(e.control.page, "Selecione uma linha para apagar!", success=False)
                return
            
            # Obter os dados da licença selecionada
            licenca_selecionada = self.result_licencas[self.selected_row_index]
            
            # Criar diálogo de confirmação
            def confirmar_apagar(e):
                try:
                    # Obter dados para a query
                    policial_id = self.res_pol[0]["id"] if hasattr(self.res_pol[0], "keys") else self.res_pol[0][0]
                    licenca = licenca_selecionada["licenca"] if hasattr(licenca_selecionada, "keys") else licenca_selecionada[0]
                    inicio = licenca_selecionada["inicio"] if hasattr(licenca_selecionada, "keys") else licenca_selecionada[1]
                    
                    # Query de exclusão
                    delete_query = """
                        DELETE FROM licencas 
                        WHERE policial_id = ? AND licenca = ? AND inicio = ?
                    """
                    
                    # Executar a exclusão
                    success = self.app.db.execute_command(delete_query, (policial_id, licenca, inicio))
                    
                    if success:
                        show_alert_dialog(e.control.page, "Licença apagada com sucesso!", success=True)
                        # Limpar seleção
                        self.selected_row_index = None
                        # Atualizar a tabela
                        atualizar_tabela()
                    else:
                        show_alert_dialog(e.control.page, "Erro ao apagar a licença!", success=False)
                        
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
                    f"Tem certeza que deseja apagar esta licença?\n\n"
                    f"Tipo: {licenca_selecionada['licenca'] if hasattr(licenca_selecionada, 'keys') else licenca_selecionada[0]}\n"
                    f"Início: {_format_date(licenca_selecionada['inicio'] if hasattr(licenca_selecionada, 'keys') else licenca_selecionada[1])}\n"
                    f"Fim: {_format_date(licenca_selecionada['fim'] if hasattr(licenca_selecionada, 'keys') else licenca_selecionada[2])}"
                ),
                actions=[
                    ft.TextButton("Cancelar", on_click=cancelar_apagar),
                    ft.TextButton("Apagar", on_click=confirmar_apagar, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            e.control.page.open(dlg_confirmacao)


        def exportar_pdf(e):
            try:
                # Ler o diretório de saída do arquivo de configuração
                with open("assets/json/app_config.json", "r", encoding='utf-8') as f:
                    config = json.load(f)
                    output_dir = config.get("output_dir")
                
                if not output_dir:
                    show_alert_dialog(e.control.page, "Diretório de saída não configurado!", success=False)
                    return
                
                if not self.tabela_rows:
                    show_alert_dialog(e.control.page, "Não há dados para exportar!", success=False)
                    return

                # Criar o diretório se não existir
                os.makedirs(output_dir, exist_ok=True)

                # Definir o nome do arquivo PDF usando encoding apropriado
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                pdf_name = f"ausencias_{timestamp}.pdf"
                pdf_path = os.path.join(output_dir, pdf_name)
                
                # Criar o documento PDF em modo paisagem
                doc = SimpleDocTemplate(
                    pdf_path,
                    pagesize=landscape(A4),
                    rightMargin=30,
                    leftMargin=30,
                    topMargin=30,
                    bottomMargin=30
                )

                # Lista de elementos para o PDF
                elements = []

                # Adicionar a logo
                logo_path = os.path.join(os.getcwd(), "assets", "icons", "logoNUVIG.png")
                if os.path.exists(logo_path):
                    img = Image(logo_path, width=5*cm, height=(5*(3/4)*cm))
                    elements.append(img)

                # Adicionar espaço após a logo
                elements.append(Spacer(1, 20))

                # Registrar a fonte DejaVu que suporta caracteres Unicode
                font_path = os.path.join(os.getcwd(), "assets", "fonts", "DejaVuSans.ttf")
                if not os.path.exists(font_path):
                    # Se a fonte não existir, usar Helvetica (que é a fonte padrão)
                    font_name = "Helvetica"
                else:
                    # Registrar a fonte DejaVu
                    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                    font_name = "DejaVuSans"

                # Preparar os dados da tabela
                headers = ["Nome", "QRA", "Licença", "Início", "Fim", "Dias", "Retorno"]
                data = [headers]  # Primeira linha com os cabeçalhos

                # Adicionar os dados das linhas
                for row in self.tabela_rows:
                    row_data = []
                    for cell in row.cells:
                        row_data.append(cell.content.value)
                    data.append(row_data)

                # Criar a tabela
                table = Table(data)
                
                # Estilo da tabela
                style = TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONT', (0, 0), (-1, 0), font_name+'-Bold' if font_name == 'Helvetica' else font_name),
                    ('FONT', (0, 1), (-1, -1), font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('ROWHEIGHT', (0, 0), (-1, -1), 20),
                ])
                
                table.setStyle(style)
                elements.append(table)

                # Gerar o PDF
                doc.build(elements)
                
                show_alert_dialog(
                    e.control.page,
                    f"PDF exportado com sucesso para:\n{pdf_path}",
                    success=True
                )

            except Exception as ex:
                show_alert_dialog(e.control.page, f"Erro ao exportar PDF: {str(ex)}", success=False)


        btn_apagar = ft.ElevatedButton(
            text="Apagar",
            icon=ft.Icons.DELETE,
            width=150,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.RED,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.RED),
            ),
            on_click=apagar_licenca
        )

        btn_relatorio = ft.ElevatedButton(
            text="Exportar PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            width=btn_apagar.width,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.BLACK),
            ),
            on_click=exportar_pdf
        )

        row_botoes = ft.Row(
            [btn_apagar, btn_relatorio],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20
        )

        return ft.Column([
            titulo,
            ft.Container(height=10),
            filtros_row,
            ft.Container(height=16),
            tabela_container,
            row_botoes,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.START, spacing=4)
