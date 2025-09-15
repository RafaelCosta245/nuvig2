import flet as ft

from .base_screen import BaseScreen
import flet as ft

class DisponibilidadeFeriasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "disponibilidade_ferias"
        self.selected_opcao = "A"
        self.selected_ano = "2025"

    def get_content(self) -> ft.Control:
        titulo = ft.Text(
            "Consulte a disponibilidade para férias",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        dropdown_opcao = ft.Dropdown(
            options=[
                ft.dropdown.Option("A"),
                ft.dropdown.Option("B"),
                ft.dropdown.Option("C"),
                ft.dropdown.Option("D"),
            ],
            value=self.selected_opcao,
            width=120,
        )
        dropdown_ano = ft.Dropdown(
            options=[
                ft.dropdown.Option(str(ano)) for ano in range(2025, 2031)
            ],
            value=self.selected_ano,
            width=120,
        )
        row_dropdowns = ft.Row(
            controls=[dropdown_opcao, dropdown_ano],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30,
        )

        tabela_container = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Tabela de disponibilidade será exibida aqui.", size=16)
                ],
                spacing=10,
            ),
            width=600,
            height=350,
            bgcolor=ft.Colors.GREY_100,
            border_radius=10,
            padding=20,
            alignment=ft.alignment.top_center,
        )
        tabela_scroll = ft.ListView(
            controls=[tabela_container],
            expand=True,
            auto_scroll=False,
        )

        main_column = ft.Column(
            controls=[
                titulo,
                row_dropdowns,
                tabela_scroll,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
        return main_column
