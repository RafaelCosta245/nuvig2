import flet as ft

class NavBar(ft.Row):
    def __init__(self, on_nav, selected_nav=None, authenticated=False, on_cadastro_option=None):
        self.on_nav = on_nav
        self.selected_nav = selected_nav
        self.authenticated = authenticated
        self.on_cadastro_option = on_cadastro_option
        
        super().__init__(
            controls=self._build_controls(),
            alignment=ft.MainAxisAlignment.START,
            spacing=0
        )
    
    def _build_controls(self):
        nav_items = [
            ("Home", "home"),
            ("Calendário", "calendario"),
            ("Cadastro", "cadastro"),
            ("Extras", "extras"),
            ("Permutas", "permutas"),
            ("Compensações", "compensacoes"),
            ("Férias", "ferias"),
            ("Ausências", "ausencias"),
            ("TAC", "tac"),
            ("Banco de dados", "banco_dados"),
        ]
        
        def handle_nav(e):
            if self.on_nav:
                self.on_nav(e.control.data)
        
        return [
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
                    disabled=not self.authenticated,  # Desabilita se não autenticado
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLUE if self.selected_nav == data else (ft.Colors.GREY if not self.authenticated else ft.Colors.BLACK),
                        bgcolor=ft.Colors.BLUE_100 if self.selected_nav == data else None,
                        padding=ft.padding.symmetric(horizontal=16, vertical=8)
                    ),
                ) for label, data in nav_items
            ]
        ]
    
    def update_auth_state(self, authenticated: bool):
        """Atualiza o estado de autenticação e reconstrói os controles"""
        self.authenticated = authenticated
        self.controls.clear()
        self.controls.extend(self._build_controls())
        self.update()