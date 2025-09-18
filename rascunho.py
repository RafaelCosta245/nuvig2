import flet as ft

def main(page: ft.Page):
    # Criando o Dropdown
    dd = ft.Dropdown(
        label="Escolha uma opção",
        options=[
            ft.dropdown.Option("A"),
            ft.dropdown.Option("B"),
            ft.dropdown.Option("C"),
        ],
        value=None,  # Inicialmente sem seleção
    )

    def limpar(e):
        dd.value = None  # Limpa a seleção
        dd.hint_text = "Escolha uma opção"  # Reforça o estado inicial
        dd.update()  # Atualiza o Dropdown
        page.update()  # Atualiza a página inteira

    # Adicionando o Dropdown e o botão à página
    page.add(
        ft.Column([  # Usando Column para garantir controle
            dd,
            ft.ElevatedButton("Limpar seleção", on_click=limpar)
        ])
    )

ft.app(target=main)