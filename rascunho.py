import flet as ft

def main(page: ft.Page):
    page.title = "Itens de carregamento do Flet"
    page.scroll = "auto"

    # Lista de itens de carregamento
    itens = [
        ("ProgressBar", ft.ProgressBar(width=300)),
        ("ProgressBar indeterminado", ft.ProgressBar(width=300, value=None)),
        ("ProgressRing", ft.ProgressRing()),
        ("ProgressRing com valor", ft.ProgressRing(value=0.7)),
        ("CupertinoActivityIndicator", ft.CupertinoActivityIndicator()),
        ("CupertinoActivityIndicator grande", ft.CupertinoActivityIndicator(radius=20)),
    ]

    # Organizar em cards
    col = ft.Column(
        [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(nome, weight=ft.FontWeight.BOLD),
                            controle,
                        ]
                    ),
                    padding=15,
                )
            )
            for nome, controle in itens
        ],
        spacing=15,
        expand=True,
    )

    page.add(col)

ft.app(target=main)
