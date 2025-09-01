import flet as ft

def main(page: ft.Page):
    page.title = "Exemplo DataTable com mudança de cor"
    page.scroll = "auto"

    def mudar_cor_linha(e):
        row = e.control  # DataRow que disparou o evento
        row.selected = not row.selected  # alterna seleção manualmente

        if row.selected:
            row.color = "#90EE90"  # verde claro
            print("Linha selecionada → cor VERDE")
        else:
            row.color = None  # volta ao padrão
            print("Linha desmarcada → cor resetada")

        page.update()

    tabela = ft.DataTable(
        width=700,
        bgcolor="yellow",
        border=ft.border.all(2, "red"),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(3, "blue"),
        horizontal_lines=ft.border.BorderSide(1, "green"),
        sort_column_index=0,
        sort_ascending=True,
        heading_row_color=ft.Colors.BLACK12,
        heading_row_height=100,
        data_row_color={"hovered": "0x30FF0000"},
        show_checkbox_column=False,  # aqui desabilitei checkbox, só clique na linha
        divider_thickness=0,
        column_spacing=200,
        columns=[
            ft.DataColumn(ft.Text("Column 1")),
            ft.DataColumn(ft.Text("Column 2"), numeric=True),
        ],
        rows=[
            ft.DataRow(
                [ft.DataCell(ft.Text("A")), ft.DataCell(ft.Text("1"))],
                on_select_changed=mudar_cor_linha,
            ),
            ft.DataRow(
                [ft.DataCell(ft.Text("B")), ft.DataCell(ft.Text("2"))],
                on_select_changed=mudar_cor_linha,
            ),
        ],
    )

    page.add(tabela)

ft.app(target=main)
