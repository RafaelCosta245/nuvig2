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
        self.matricula_input = ft.TextField(label="Matrícula", width=200, on_change=self.buscar_policial, max_length=8)
        self.result_container = ft.Container()
        self.save_button = ft.ElevatedButton("Salvar Alterações", on_click=self.salvar_alteracoes, visible=False)
        return ft.Column([
            ft.Row([
                self.matricula_input
            ]),
            self.result_container,
            self.save_button
        ], spacing=20)

    def buscar_policial(self, e):
        matricula = self.matricula_input.value
        policial = self.db.get_policial_by_matricula(matricula)
        if policial:
            self.policial_id = policial.get('id')
            # Exibir todos os dados do policial encontrado
            self.campos_edicao = []
            escala_options = ["A", "B", "C", "D", "ABC", "BCD", "CDA", "DAB", "AB", "BC", "CD", "DA"]
            situacao_options = [
                ft.dropdown.Option(key="ativo", text="Ativo"),
                ft.dropdown.Option(key="inativo", text="Inativo"),
            ]
            for key, value in policial.items():
                if key == "id":
                    self.campos_edicao.append(ft.Text(f"ID: {value}", size=16))
                elif key == "escala":
                    self.campos_edicao.append(
                        ft.Dropdown(
                            label="Escala",
                            width=200,
                            options=[ft.dropdown.Option(v) for v in escala_options],
                            value=str(value)
                        )
                    )
                elif key == "situacao":
                    self.campos_edicao.append(
                        ft.Dropdown(
                            label="Situação",
                            width=200,
                            options=situacao_options,
                            value=str(value)
                        )
                    )
                else:
                    self.campos_edicao.append(ft.TextField(label=key.capitalize(), value=str(value)))
            self.result_container.content = ft.Column(self.campos_edicao)
            self.save_button.visible = True
        else:
            self.result_container.content = ft.Text("Matrícula não encontrada.", color=ft.Colors.RED)
            self.save_button.visible = False
        self.app.page.update()

    def salvar_alteracoes(self, e):
        # Extrair valores dos campos editáveis
        nome = self.campos_edicao[1].value if len(self.campos_edicao) > 1 else ""
        qra = self.campos_edicao[2].value if len(self.campos_edicao) > 2 else ""
        matricula = self.campos_edicao[3].value if len(self.campos_edicao) > 3 else ""
        escala = self.campos_edicao[4].value if len(self.campos_edicao) > 4 else ""
        situacao = self.campos_edicao[5].value if len(self.campos_edicao) > 5 else ""
        sucesso = self.db.atualizar_policial(matricula, nome, qra, escala)
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
