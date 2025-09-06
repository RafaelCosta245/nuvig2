import flet as ft

def main(page: ft.Page):
    page.title = "Tabela de Dados"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    data = [
        ["João", "25", "Engenheiro", "São Paulo", "R$5000", "Ativo"],
        ["Maria", "30", "Médica", "Rio de Janeiro", "R$8000", "Ativo"],
        ["Pedro", "28", "Professor", "Belo Horizonte", "R$4000", "Inativo"],
        ["Ana", "35", "Advogada", "Curitiba", "R$6000", "Ativo"],
        ["Lucas", "22", "Estudante", "Porto Alegre", "R$1000", "Ativo"],
        ["Clara", "40", "Arquiteta", "Salvador", "R$7000", "Inativo"],
        ["Marcos", "33", "Programador", "Fortaleza", "R$5500", "Ativo"],
        ["Sofia", "27", "Designer", "Recife", "R$4500", "Ativo"],
        ["Rafael", "29", "Contador", "Manaus", "R$5200", "Inativo"],
        ["Julia", "31", "Gerente", "Brasília", "R$6500", "Ativo"],
    ]

    def col(title: str) -> ft.DataColumn:
        return ft.DataColumn(
            ft.Container(
                content=ft.Text(title, weight=ft.FontWeight.BOLD),
                alignment=ft.alignment.center,
                expand=True,            # <- faz o header ocupar a largura da coluna
            )
        )

    def cell(value: str) -> ft.DataCell:
        return ft.DataCell(
            ft.Row([ft.Text(value)],
                   alignment=ft.MainAxisAlignment.CENTER,
                   expand=True)          # <- garante que o conteúdo também expanda
        )

    table = ft.DataTable(
        border=ft.border.all(1, ft.Colors.GREY_400),
        border_radius=10,
        heading_row_color=ft.Colors.BLUE_50,
        heading_row_height=50,
        # opcional: reduzir espaços extras entre colunas
        # column_spacing=0,
        columns=[
            col("Nome"),
            col("Idade"),
            col("Profissão"),
            col("Cidade"),
            col("Salário"),
            col("Status"),
        ],
        rows=[
            ft.DataRow(cells=[cell(v) for v in row]) for row in data
        ],
    )

    page.add(
        ft.Container(
            content=table,
            width=page.width,
            height=page.height,
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300),
        )
    )

ft.app(target=main)
