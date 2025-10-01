import flet as ft
from .base_screen import BaseScreen


class TacScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "tac"

    def get_content(self) -> ft.Control:
        header = ft.Container(
            content=ft.Text(
                "Termos de ajuste de conduta - TAC",
                size=28,
                color=ft.Colors.BLACK,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            padding=ft.padding.only(bottom=20),
            alignment=ft.alignment.center
        )


        def card_cadastrar_tac() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("📝 Cadastrar TAC", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text("   Agendar novo TAC", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=15),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("cadastrar_tac"),
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

        def card_consultar_tac() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("🔎 TAC's Agendados", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text("   Pesquise os TAC's já agendadas", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=15),
                        ft.TextButton(
                            text="Abrir",
                            icon=ft.Icons.ARROW_FORWARD,
                            on_click=lambda e: self.navigate_to("consultar_tac"),
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
                card_cadastrar_tac(),
                card_consultar_tac()
            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)


