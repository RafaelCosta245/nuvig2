import flet as ft
import re

def main(page: ft.Page):
    page.title = "Todos os ícones do Flet"
    page.padding = 20
    page.scroll = "adaptive"

    # Pega todos os atributos de ft.Icons que são strings (nomes de ícones)
    icon_names = [name for name in dir(ft.Icons) if name.isupper()]
    icon_names.sort()

    # Agrupa ícones por categoria (prefixo antes do "_")
    categories = {}
    for name in icon_names:
        prefix = name.split("_")[0]  # ex: SAVE_ALT -> SAVE
        categories.setdefault(prefix, []).append(name)

    # Container principal que vai trocar entre "categorias" e "ícones"
    content_area = ft.Column(expand=True)

    def show_categories():
        """Mostra os cards de categorias"""
        content_area.controls.clear()
        content_area.controls.append(
            ft.Text("Categorias de Ícones", size=20, weight=ft.FontWeight.BOLD)
        )

        grid = ft.GridView(
            expand=True,
            runs_count=4,
            max_extent=160,
            spacing=10,
            run_spacing=10,
        )

        for cat, items in categories.items():
            # Pega o primeiro ícone da categoria como "amostra"
            sample_icon = getattr(ft.Icons, items[0])
            grid.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(sample_icon, size=40, color=ft.Colors.BLUE),
                            ft.Text(cat, size=12, text_align=ft.TextAlign.CENTER),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    border=ft.border.all(1, ft.Colors.GREY_400),
                    border_radius=10,
                    padding=10,
                    ink=True,
                    on_click=lambda e, c=cat: show_icons(c),
                )
            )

        content_area.controls.append(grid)
        page.update()

    def show_icons(category):
        """Mostra todos os ícones de uma categoria"""
        content_area.controls.clear()
        content_area.controls.append(
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda e: show_categories()),
                ft.Text(f"Categoria: {category}", size=18, weight=ft.FontWeight.BOLD),
            ])
        )

        grid = ft.GridView(
            expand=True,
            runs_count=6,
            max_extent=120,
            spacing=10,
            run_spacing=10,
        )

        for name in categories[category]:
            icon_value = getattr(ft.Icons, name)
            grid.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(icon_value, size=32, color=ft.Colors.BLUE),
                            ft.Text(name, size=10, text_align=ft.TextAlign.CENTER, no_wrap=True),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    border_radius=8,
                    padding=5,
                )
            )

        content_area.controls.append(grid)
        page.update()

    # Mostra categorias ao abrir
    show_categories()
    page.add(content_area)

ft.app(target=main)
