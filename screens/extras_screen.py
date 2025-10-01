import flet as ft
from .base_screen import BaseScreen

class ExtrasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "extras"
        
    def get_content(self) -> ft.Control:
        header = ft.Container(
            content=ft.Text(
                "Extras",
                size=28,
                color=ft.Colors.BLACK,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            padding=ft.padding.only(bottom=20),
            alignment=ft.alignment.center
        )

        def card_cadastrar_extra() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("📝 Cadastrar Extra", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Agendar novo extra", size=12, color=ft.Colors.GREY),
                        ft.Container(height=10),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("cadastrar_extra"),
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

        def card_consultar_extras() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("🔎 Extras Agendadas", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Pesquise os extras já agendados", size=12, color=ft.Colors.GREY),
                        ft.Container(height=10),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("consultar_extras"),
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

        def card_relatorios() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("📊 Relatórios", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Relatórios das Extras", size=12, color=ft.Colors.GREY),
                        ft.Container(height=10),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            #on_click=lambda e: self.navigate_to("consultar_extras"),
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

        def card_cadastro_horas() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("🕒➕ Banco de extras", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Adicione horas ao banco", size=12, color=ft.Colors.GREY),
                        ft.Container(height=10),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("banco_extras"),
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

        def card_disponibilidade() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("✅ Disponibilidade", size=18, weight=ft.FontWeight.BOLD),
                        ft.Text("Datas disponíveis para Extras", size=12, color=ft.Colors.GREY),
                        ft.Container(height=10),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("disponibilidade_extras"),
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

        return ft.Column([
            header,
            ft.Row([
                card_cadastrar_extra(),
                card_consultar_extras(),
                card_relatorios(),
                card_cadastro_horas(),
                card_disponibilidade()
            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)


