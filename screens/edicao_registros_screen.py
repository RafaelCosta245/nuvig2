import flet as ft
from database.database_manager import DatabaseManager

class EdicaoRegistrosScreen:
    def __init__(self, app):
        self.app = app
        self.db = app.db
        self.navigation_callback = None

    def set_navigation_callback(self, callback):
        self.navigation_callback = callback

    def get_content(self):
        # Campo de pesquisa de matrícula
        self.matricula_pesquisa = ft.TextField(label="Matrícula", width=200, on_change=self.buscar_policial, max_length=8)

        # Texto explicativo
        texto_explicativo = ft.Text("Pesquise pela matrícula", size=14, color=ft.Colors.BLACK,
                                    text_align=ft.TextAlign.CENTER)

        # Campos do formulário
        self.nome_field = ft.TextField(label="Nome", width=400)
        self.qra_field = ft.TextField(label="QRA", width=self.nome_field.width)
        self.matricula_field = ft.TextField(label="Matrícula", width=self.nome_field.width, read_only=True)
        
        escala_options = ["A", "B", "C", "D", "ABC", "BCD", "CDA", "DAB", "AB", "BC", "CD", "DA"]
        self.escala_field = ft.Dropdown(label="Escala", width=self.nome_field.width, options=[ft.dropdown.Option(e) for e in escala_options])
        
        self.situacao_field = ft.Dropdown(label="Situação", width=self.nome_field.width, options=[ft.dropdown.Option("ativo"), ft.dropdown.Option("inativo")])
        self.data_inicio_field = ft.TextField(label="Data de Início", width=self.nome_field.width, hint_text="dd/mm/aaaa")
        
        # Função para aplicar máscara de data
        def mascara_data_inicio(e):
            valor = ''.join([c for c in self.data_inicio_field.value if c.isdigit()])
            novo_valor = ''
            if len(valor) > 0:
                novo_valor += valor[:2]
            if len(valor) > 2:
                novo_valor += '/' + valor[2:4]
            if len(valor) > 4:
                novo_valor += '/' + valor[4:8]
            self.data_inicio_field.value = novo_valor
            e.control.page.update()
        
        self.data_inicio_field.on_change = mascara_data_inicio
        # Dropdown de unidade
        self.id_field = ft.TextField(label="ID", width=self.nome_field.width, read_only=True)
        unidades_opcoes = [ft.dropdown.Option(u) for u in self.db.buscar_unidades()]
        self.unidade_field = ft.Dropdown(label="Unidade", width=self.nome_field.width, options=unidades_opcoes)
        self.save_button = ft.ElevatedButton(
            text="Salvar Alterações",
            icon=ft.Icons.SAVE,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
            ),
            on_click=self.salvar_alteracoes,
            visible=True
        )

        # Layout inicial: todos os campos visíveis
        return ft.Column([
            ft.Row([
                ft.Text("Pesquise pela matrícula", size=14, color=ft.Colors.BLACK,weight=ft.FontWeight.BOLD ,text_align=ft.TextAlign.CENTER)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.matricula_pesquisa], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.nome_field, self.qra_field], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.matricula_field, self.escala_field], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.situacao_field, self.data_inicio_field], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.unidade_field, self.id_field], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([self.save_button], alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=20, alignment=ft.MainAxisAlignment.START)

    def buscar_policial(self, e):
        matricula = self.matricula_pesquisa.value
        policial = self.db.get_policial_by_matricula(matricula)
        if policial:
            self.policial_id = policial.get('id')
            self.nome_field.value = str(policial.get('nome', ''))
            self.qra_field.value = str(policial.get('qra', ''))
            self.matricula_field.value = str(policial.get('matricula', ''))
            self.escala_field.value = str(policial.get('escala', ''))
            self.situacao_field.value = str(policial.get('situacao', ''))
            # Formatar data de início (coluna 'inicio') para dd/mm/aaaa
            inicio_val = policial.get('inicio', '')
            if inicio_val and len(inicio_val) == 10 and '-' in inicio_val:
                partes = inicio_val.split('-')
                self.data_inicio_field.value = f"{partes[2]}/{partes[1]}/{partes[0]}"
            else:
                self.data_inicio_field.value = str(inicio_val)
            self.unidade_field.value = str(policial.get('unidade', ''))
        else:
            self.nome_field.value = ""
            self.qra_field.value = ""
            self.matricula_field.value = ""
            self.escala_field.value = ""
            self.situacao_field.value = ""
            self.data_inicio_field.value = ""
            self.unidade_field.value = ""
        self.app.page.update()

    def salvar_alteracoes(self, e):
        nome = self.nome_field.value
        qra = self.qra_field.value
        matricula = self.matricula_field.value
        # Converter data de início para aaaa-mm-dd
        inicio = self.data_inicio_field.value
        if inicio and len(inicio) == 10 and '/' in inicio:
            partes = inicio.split('/')
            inicio_sql = f"{partes[2]}-{partes[1]}-{partes[0]}"
        else:
            inicio_sql = inicio
        escala = self.escala_field.value
        situacao = self.situacao_field.value
        unidade = self.unidade_field.value
        sucesso = self.db.atualizar_policial(matricula, nome, qra, escala, situacao, inicio_sql, unidade)
        page = self.app.page
        if sucesso:
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Sucesso", color=ft.Colors.GREEN),
                content=ft.Text("Dados alterados com sucesso."),
                actions=[
                    ft.TextButton(
                        "OK",
                        on_click=lambda e: page.close(dlg_modal)
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(dlg_modal)
        else:
            erro_msg = getattr(self.db, 'last_error', None) or "Erro ao alterar dados"
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text("Erro", color=ft.Colors.RED),
                content=ft.Text(erro_msg),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: page.close(dlg_modal))
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.open(dlg_modal)
        self.app.page.update()
