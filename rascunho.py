import flet as ft

def main(page: ft.Page):
    page.title = "Importar Banco de Dados"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "start"

    status_text = ft.Text("", color="green")

    def importar_local(e):
        status_text.value = "Arquivo local importado com sucesso!"
        page.update()

    def importar_nuvem(e):
        status_text.value = "Arquivo da nuvem importado com sucesso!"
        page.update()

    card_local = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.UPLOAD_FILE, size=50, color="blue"),
                    ft.Text("Importar do Computador", size=18, weight="bold"),
                    ft.Text("Selecione um arquivo .db do seu dispositivo."),
                    ft.ElevatedButton("Escolher Arquivo", icon=ft.Icons.FOLDER_OPEN, on_click=importar_local),
                ],
                horizontal_alignment="center",
                spacing=10,
            ),
            padding=20,
            width=250,
        ),
    )

    card_nuvem = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.CLOUD, size=50, color="purple"),
                    ft.Text("Importar da Nuvem", size=18, weight="bold"),
                    ft.Text("Busque um arquivo salvo no Google Drive."),
                    ft.ElevatedButton("Procurar na Nuvem", icon=ft.Icons.CLOUD_DOWNLOAD, on_click=importar_nuvem),
                ],
                horizontal_alignment="center",
                spacing=10,
            ),
            padding=20,
            width=250,
        ),
    )

    page.add(
        ft.Text("Importar Banco de Dados", size=24, weight="bold"),
        ft.Divider(),
        ft.ResponsiveRow(
            [
                ft.Container(card_local, col={"xs": 12, "md": 6}),
                ft.Container(card_nuvem, col={"xs": 12, "md": 6}),
            ],
            alignment="center",
            spacing=20,
        ),
        status_text,
        ft.Row(
            [
                ft.ElevatedButton("Voltar", icon=ft.Icons.ARROW_BACK),
            ],
            alignment="start",
        ),
    )

ft.app(target=main)
