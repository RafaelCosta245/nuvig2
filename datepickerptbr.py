import flet as ft
import datetime

def main(page: ft.Page):
    # Configurar a localidade para português do Brasil
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("pt", "BR"),  # Português do Brasil
            ft.Locale("en", "US")   # Inglês como fallback (opcional)
        ],
        current_locale=ft.Locale("pt", "BR")  # Define pt-BR como padrão
    )

    # Função para lidar com a seleção de data
    def change_date(e):
        selected_date.value = f"Data selecionada: {date_picker.value.strftime('%d/%m/%Y')}"
        page.update()

    def date_picker_dismissed(e):
        selected_date.value = f"DatePicker fechado, valor: {date_picker.value.strftime('%d/%m/%Y') if date_picker.value else 'Nenhuma data selecionada'}"
        page.update()

    # Configurar o DatePicker
    today = datetime.datetime.now().date()
    next_year = today + datetime.timedelta(days=365)

    date_picker = ft.DatePicker(
        on_change=change_date,
        on_dismiss=date_picker_dismissed,
        first_date=today,
        last_date=next_year,
    )

    # Adicionar o DatePicker como um diálogo
    page.overlay.append(date_picker)

    # Texto para exibir a data selecionada
    selected_date = ft.Text("Nenhuma data selecionada")

    # Função para abrir o DatePicker
    def open_date_picker(e):
        date_picker.open = True  # Abre o DatePicker
        page.update()

    # Botão para abrir o DatePicker
    date_button = ft.ElevatedButton(
        "Selecionar data",
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=open_date_picker,
    )

    # Adicionar os controles à página
    page.add(
        date_button,
        selected_date
    )
    page.update()

ft.app(target=main)