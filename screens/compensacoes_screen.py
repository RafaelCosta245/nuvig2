import flet as ft
from .base_screen import BaseScreen


class CompensacoesScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "compensacoes"

    def get_content(self) -> ft.Control:
        header = ft.Container(
            content=ft.Text(
                "Compensações",
                size=28,
                color=ft.Colors.BLACK,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            padding=ft.padding.only(bottom=20),
            alignment=ft.alignment.center
        )

        def card_cadastrar_compensacao() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("📝 Cadastrar Compensação", size=18, weight=ft.FontWeight.BOLD,text_align=ft.TextAlign.CENTER),
                        ft.Text("   Agendar nova compensação", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=15),
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
                width=310,
                height=140
            )

        def card_consultar_compensacao() -> ft.Control:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("🔎 Compensações Agendadas", size=18, weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER),
                        ft.Text("   Pesquise as compensações já agendadas", size=12, color=ft.Colors.GREY,
                                text_align=ft.TextAlign.CENTER),
                        ft.Container(height=15),
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
                width=300,
                height=140
            )

        return ft.Column([
            header,
            ft.Row([
                card_cadastrar_compensacao(),
                card_consultar_compensacao()
            ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)


