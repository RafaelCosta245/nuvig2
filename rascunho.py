import flet as ft

def main(page: ft.Page):
    page.title = "Reset Dropdown Example"
    page.padding = 40

    def dropdown_changed(e):
        # Exibe o valor selecionado
        print(f"Valor selecionado: {dropdown.value}")
        # Reseta o dropdown
        dropdown.value = None  # Define o valor como None para "limpar"
        page.update()  # Atualiza a interface

    # Cria o dropdown com uma opção de placeholder
    dropdown = ft.Dropdown(
        label="Escolha uma opção",
        options=[
            ft.dropdown.Option(key=None, text="Selecione uma opção"),  # Placeholder
            ft.dropdown.Option("1", "Opção 1"),
            ft.dropdown.Option("2", "Opção 2"),
            ft.dropdown.Option("3", "Opção 3"),
        ],
        value=None,  # Estado inicial vazio
        on_change=dropdown_changed  # Chama a função ao mudar a seleção
    )

    # Botão opcional para resetar manualmente
    def reset_dropdown(e):
        dropdown.value = None
        page.update()

    reset_button = ft.ElevatedButton("Resetar Dropdown", on_click=reset_dropdown)

    # Adiciona o dropdown e o botão à página
    page.add(dropdown, reset_button)

ft.app(target=main)