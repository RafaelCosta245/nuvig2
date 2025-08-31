import flet as ft
from .base_screen import BaseScreen

class CadastroScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "cadastro"

    def ir_para_cadastro_policial(self, e):
        if self.navigation_callback:
            self.navigation_callback("cadastro_policial")
import flet as ft
from .base_screen import BaseScreen

class CadastroScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "cadastro"

    def ir_para_cadastro_policial(self, e):
        if self.navigation_callback:
            self.navigation_callback("cadastro_policial")

    def get_content(self) -> ft.Control:
        header = ft.Container(
            content=ft.Text(
                "Cadastros",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLACK,
                text_align=ft.TextAlign.CENTER
            ),
            padding=ft.padding.only(bottom=20),
            alignment=ft.alignment.center
        )

        def card_cadastro_policial() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("👮 Cadastrar Policial", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Gerenciar cadastro de policiais", size=12, color=ft.Colors.GREY),
                        ft.Container(height=10),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("cadastro_policial"),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=5,
                ),
                padding=ft.padding.all(8),
                border=ft.border.all(1, ft.Colors.GREY),
                border_radius=12,
                bgcolor=ft.Colors.WHITE,
                width=260,
                height=140
            )

        grid = ft.Row(
            controls=[card_cadastro_policial()],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            wrap=True
        )

        card_cadastro = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("👮 Cadastrar Policial", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text("Cadastrar novo PP", size=12, color=ft.Colors.GREY),
                    #ft.Icon(ft.Icons.PERSON_ADD, size=40),
                    ft.TextButton(
                        text="Abrir",
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=self.ir_para_cadastro_policial
                    )
                    #ft.ElevatedButton("Cadastrar", on_click=self.ir_para_cadastro_policial)
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.padding.all(8),
                border=ft.border.all(1, ft.Colors.GREY),
                border_radius=12,
                bgcolor=ft.Colors.WHITE,
                width=260,
                height=140
            )
        )
        card_alterar = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("📝 Alterar Cadastro", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Alterar dados do PP", size=12, color=ft.Colors.GREY),
                    #ft.Icon(ft.Icons.EDIT, size=40),
                    #ft.ElevatedButton("Alterar", on_click=self.ir_para_edicao_registros)
                    ft.TextButton(
                        text="Abrir",
                        icon=ft.Icons.ARROW_FORWARD,
                        on_click=self.ir_para_edicao_registros
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER),
                padding=ft.padding.all(8),
                border=ft.border.all(1, ft.Colors.GREY),
                border_radius=12,
                bgcolor=ft.Colors.WHITE,
                width=260,
                height=140
            )
        )
        return ft.Column([
                    header,
                    ft.Row(controls=[
                        card_cadastro,
                        card_alterar
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.START)
])
    def ir_para_edicao_registros(self, e):
        if self.navigation_callback:
            self.navigation_callback("edicao_registros")


