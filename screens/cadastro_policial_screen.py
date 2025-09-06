import flet as ft
from .base_screen import BaseScreen

class CadastroPolicialScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "cadastro"

    def get_content(self) -> ft.Control:
        header = ft.Container(
            content=ft.Text(
                "Cadastrar Policial",
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
                text_align=ft.TextAlign.CENTER
            ),
            padding=ft.padding.only(bottom=20),
            alignment=ft.alignment.center
        )

        self.campo_nome = ft.TextField(label="Nome Completo", width=410, border_radius=4)
        self.campo_qra = ft.TextField(label="QRA", width=200, border_radius=4)
        self.campo_matricula = ft.TextField(label="Matrícula", width=200, border_radius=4,max_length=8)
        self.campo_inicio = ft.TextField(label="Último Plantão", width=200, border_radius=4)


        escala_options = ["A", "B", "C", "D", "ABC", "BCD", "CDA", "DAB", "AB", "BC", "CD", "DA"]
        self.campo_escala = ft.Dropdown(
            label="Escala",
            width=200,
            options=[ft.dropdown.Option(v) for v in escala_options]
        )

        # Armazena valores em minúsculo para aderir ao CHECK constraint do banco
        self.campo_situacao = ft.Dropdown(
            label="Situação",
            width=200,
            options=[
                ft.dropdown.Option(key="ativo", text="Ativo"),
                ft.dropdown.Option(key="inativo", text="Inativo"),
            ]
        )
        unidades_options = [
            "UP 01",
            "UP 02",
            "UP 03",
            "UP 04",
            "UP 05 - CEPIS",
            "UP 06 - UPECT",
            "UP SOBREIRA",
            "UPPOO 2",
            "UPTOC",
            "UPF",
            "UP IMELDA",
            "UP AQUIRAZ",
            "UP MAX",
            "UPSPOl",
            "UP STENIO GOMES",
            "NUVIG",
            "GAP"
        ]
        self.campo_unidade = ft.Dropdown(
            label="UP",
            width=200,
            options=[ft.dropdown.Option(v) for v in unidades_options]
            )

        botoes = ft.Row(
            controls=[
                ft.ElevatedButton(text="   Cadastrar   ",
                                  icon=ft.Icons.SAVE,
                                  bgcolor=ft.Colors.GREEN,
                                  color=ft.Colors.WHITE,
                                  on_click=self.on_salvar,),
                ft.OutlinedButton(text="Cancelar",
                                  icon=ft.Icons.CANCEL,
                                  on_click=lambda e: self.navigate_to("cadastro")
                                  )

            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.CENTER
        )

        form = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[self.campo_nome], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=5),
                    ft.Row(controls=[self.campo_qra, self.campo_matricula], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    ft.Container(height=5),
                    ft.Row(controls=[self.campo_escala, self.campo_situacao], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                    ft.Container(height=5),
                    ft.Row(controls=[self.campo_inicio, self.campo_unidade],
                           alignment=ft.MainAxisAlignment.CENTER,
                           spacing=5),
                    ft.Container(height=10),
                    botoes
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.all(20),
            border=ft.border.all(1, ft.Colors.GREY),
            border_radius=12,
            bgcolor=ft.Colors.WHITE,
            width=600

        )

        return ft.Column(
            controls=[header, form],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

    def on_salvar(self, e):
        nome = (self.campo_nome.value or "").strip()
        qra = (self.campo_qra.value or "").strip()
        matricula = (self.campo_matricula.value or "").strip()
        escala = (self.campo_escala.value or "").strip()
        situacao = (self.campo_situacao.value or "").strip().lower()
        inicio = (self.campo_inicio.value or "").strip()
        unidade = (self.campo_unidade.value or "").strip()

        if not nome:
            self.show_error("Informe o nome")
            return
        if not escala:
            self.show_error("Selecione a escala")
            return
        if not situacao:
            self.show_error("Selecione a situação")
            return
        if not inicio:
            self.show_error("Informe data de início do último plantão")
            return
        if not unidade:
            self.show_error("Selecione a UP do policial")
            return

        sucesso = self.app.db.inserir_policial(nome=nome,
                                               qra=qra,
                                               matricula=matricula,
                                               escala=escala,
                                               situacao=situacao,
                                               inicio=inicio,
                                               unidade=unidade)
        if sucesso:
            self.app.db.log_system_action(
                action="cadastro_policial",
                description=f"Cadastrado policial {nome} ({matricula})",
                module="cadastro"
            )
            # Exibir dialog modal e recarregar a tela SOMENTE após o fechamento
            try:
                if hasattr(self.app, 'page') and self.app.page:
                    page = self.app.page
                    dlg_modal = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Sucesso"),
                        content=ft.Text("Dados do policial salvos com sucesso."),
                        actions=[
                            ft.TextButton(
                                "OK",
                                on_click=lambda e: (page.close(dlg_modal), self._reload_screen())
                            )
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.open(dlg_modal)
                else:
                    self.show_success("Dados do policial salvos com sucesso.")
                    self._reload_screen()
            except Exception:
                self.show_success("Dados do policial salvos com sucesso.")
                self._reload_screen()
        else:
            erro_msg = getattr(self.app.db, 'last_error', None) or "Erro ao salvar policial"
            try:
                if hasattr(self.app, 'page') and self.app.page:
                    page = self.app.page
                    dlg_modal = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Erro"),
                        content=ft.Text(erro_msg),
                        actions=[ft.TextButton("OK", on_click=lambda e: page.close(dlg_modal))],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.open(dlg_modal)
                else:
                    self.show_error(erro_msg)
            except Exception:
                self.show_error(erro_msg)

    def _reload_screen(self):
        # Recria a tela para garantir que todos os controles sejam reinicializados
        try:
            # Reinstancia a tela no dicionário de telas e navega para ela
            from .cadastro_policial_screen import CadastroPolicialScreen
            self.app.screens["cadastro_policial"] = CadastroPolicialScreen(self.app)
            self.navigate_to("cadastro_policial")
        except Exception:
            # Fallback: apenas limpar campos
            self.campo_nome.value = ""
            self.campo_qra.value = ""
            self.campo_matricula.value = ""
            self.campo_escala.value = None
            self.campo_situacao.value = None
            self.campo_nome.update(); self.campo_qra.update(); self.campo_matricula.update(); self.campo_escala.update(); self.campo_situacao.update()


