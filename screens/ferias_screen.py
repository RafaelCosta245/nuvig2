import flet as ft
from .base_screen import BaseScreen


class FeriasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "ferias"

    def get_content(self) -> ft.Control:
        header = ft.Container(
            content=ft.Text(
                "Férias",
                size=28,
                color=ft.Colors.BLACK,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            padding=ft.padding.only(bottom=20),
            alignment=ft.alignment.center
        )


        def card_cadastrar_ferias() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("📝 Cadastrar Férias", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text("   Agendar novo período de férias", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=15),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("cadastrar_ferias"),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=5,
                ),
                padding=ft.padding.all(8),
                border=ft.border.all(1, ft.Colors.GREY),
                border_radius=12,
                bgcolor=ft.Colors.WHITE,
                width=310,
                height=140
            )

        def card_consultar_ferias() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("🔎 Férias Agendadas", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text("   Pesquise as férias já agendadas", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=15),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("consultar_ferias"),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    spacing=5,
                ),
                padding=ft.padding.all(8),
                border=ft.border.all(1, ft.Colors.GREY),
                border_radius=12,
                bgcolor=ft.Colors.WHITE,
                width=300,
                height=140
            )

        return ft.Column([
            header,
            ft.Row([
                card_cadastrar_ferias(),
                card_consultar_ferias()
            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
