import flet as ft

def NavBar(on_nav, selected_nav=None, on_cadastro_option=None):
    nav_items = [
        ("Home", "home"),
        ("Calendário", "calendario"),
        ("Cadastro", "cadastro"),
        ("Extras", "extras"),
        ("Permutas", "permutas"),
        ("Compensações", "compensacoes"),
        ("Férias", "ferias"),
        ("Ausências", "ausencias"),
        ]
    def handle_nav(e):
        if on_nav:
            on_nav(e.control.data)
    def handle_cadastro(e):
        if on_nav:
            on_nav("cadastro")
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Row([
                    ft.Text("NUVIG", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.only(left=10),
            ),
            ft.Container(expand=True),
            *[
                ft.TextButton(
                    text=label,
                    data=data,
                    on_click=handle_nav,
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLUE if selected_nav == data else ft.Colors.BLACK,
                        bgcolor=ft.Colors.BLUE_100 if selected_nav == data else None,
                        padding=ft.padding.symmetric(horizontal=16, vertical=8)),
                ) for label, data in nav_items
            ]
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=0
    )