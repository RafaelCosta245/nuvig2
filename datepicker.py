import flet as ft
import datetime


def main(page: ft.Page):
    page.title = "DatePicker Example"
    page.locale_configuration = ft.Locale(language_code="pt", country_code="BR")

    class DatePickerExample(ft.Column):
        def __init__(self):
            super().__init__()
            self.datepicker = ft.DatePicker(
                first_date=datetime.datetime(2025, 8, 26),
                last_date=datetime.datetime(2030, 12, 31),
                on_change=self.change_date,

            )

            self.selected_date = ft.Text()

            self.controls = [
                ft.ElevatedButton(
                    "Pick date",
                    icon=ft.Icons.CALENDAR_MONTH,
                    on_click=self.open_date_picker,
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(width=2, color=ft.Colors.BLUE),  # Borda azul
                        bgcolor=ft.Colors.WHITE,  # Fundo branco
                        color=ft.Colors.BLACK,  # Texto preto
                    )
                ),
                self.selected_date,
            ]

        def open_date_picker(self, e):
            e.control.page.open(self.datepicker)

        def change_date(self, e):
            if self.datepicker.value:
                formatted_date = self.datepicker.value.strftime("%d/%m/%Y")
                print(f"Data selecionada: {formatted_date}")  # Imprime no console
                self.selected_date.value = f"Selected date: {formatted_date}"
                e.control.page.update()

        def did_mount(self):
            self.page.overlay.append(self.datepicker)
            self.page.update()

        def will_unmount(self):
            self.page.overlay.remove(self.datepicker)
            self.page.update()

    page.add(DatePickerExample())


ft.app(target=main)