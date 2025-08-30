import flet as ft
from typing import Callable, Optional

class BaseScreen:
    """Classe base para todas as telas do sistema"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.navigation_callback: Optional[Callable] = None
        self.page: Optional[ft.Page] = None
        self.current_nav = "home"  # Navegação atual
        
    def set_navigation_callback(self, callback: Callable):
        """Define o callback de navegação"""
        self.navigation_callback = callback
        
    def navigate_to(self, screen_name: str):
        """Navega para uma tela específica"""
        if self.navigation_callback:
            self.navigation_callback(screen_name)
            
    def get_content(self) -> ft.Control:
        """Retorna apenas o conteúdo da tela (sem navbar) - deve ser implementado pelas classes filhas"""
        raise NotImplementedError("Subclasses devem implementar get_content()")
        
    def show_message(self, message: str, color: str = "green"):
        """Mostra uma mensagem para o usuário"""
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=color,
                    duration=3000
                )
            )
            
    def show_error(self, message: str):
        """Mostra uma mensagem de erro"""
        self.show_message(message, "red")
        
    def show_success(self, message: str):
        """Mostra uma mensagem de sucesso"""
        self.show_message(message, "green")
        
    def show_info(self, message: str):
        """Mostra uma mensagem informativa"""
        self.show_message(message, "blue")
        
    def create_header(self, title: str) -> ft.Container:
        """Cria um cabeçalho padrão para as telas"""
        return ft.Container(
            content=ft.Text(
                title,
                size=24,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE
            ),
            padding=ft.padding.only(bottom=20),
            alignment=ft.alignment.center
        )
        
    def create_button(self, text: str, on_click: Callable, 
                     color: str = ft.Colors.BLUE, 
                     width: int = 200) -> ft.ElevatedButton:
        """Cria um botão padrão"""
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            bgcolor=color,
            color=ft.Colors.WHITE,
            width=width,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8)
            )
        )
        
    def create_text_field(self, label: str, hint: str = "", 
                         password: bool = False, 
                         width: int = 300) -> ft.TextField:
        """Cria um campo de texto padrão"""
        return ft.TextField(
            label=label,
            hint_text=hint,
            password=password,
            width=width,
            border_radius=8,
            border_color=ft.Colors.BLUE,
            focused_border_color=ft.Colors.BLUE
        )
