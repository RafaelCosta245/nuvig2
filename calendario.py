import flet as ft
import calendar
from datetime import date




def Calendario(ano, mes, on_day_click=None, width=400, height=300, text_color="blue"):
    # Estado interno
    state = {"ano": ano, "mes": mes}

    def atualizar_calendario():
        month_title_text.value = f"{calendar.month_name[state['mes']]} {state['ano']}"
        month_title_text.update()
        # Recria as linhas
        linhas = build_linhas()
        linhas_container.controls.clear()
        linhas_container.controls.extend(linhas)
        linhas_container.update()

    def prev_month(e):
        if state["mes"] == 1:
            state["mes"] = 12
            state["ano"] -= 1
        else:
            state["mes"] -= 1
        atualizar_calendario()

    def next_month(e):
        if state["mes"] == 12:
            state["mes"] = 1
            state["ano"] += 1
        else:
            state["mes"] += 1
        atualizar_calendario()

    def build_linhas():
        calendar.setfirstweekday(calendar.SUNDAY)
        matriz = calendar.monthcalendar(state["ano"], state["mes"])
        linhas = []
        for semana in matriz:
            cells = []
            for dia in semana:
                if dia == 0:
                    cells.append(ft.Container(width=60, height=40))
                else:
                    cells.append(
                        ft.TextButton(
                            text=str(dia),
                            width=60,
                            height=40,
                            on_click=lambda e, d=dia: on_day_click(d) if on_day_click else None
                        )
                    )
            linhas.append(ft.Row(controls=cells, spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        return linhas

    nome_mes = calendar.month_name[state["mes"]]
    month_title_text = ft.Text(f"{nome_mes} {state['ano']}", size=24, weight=ft.FontWeight.BOLD, color=text_color)
    header = ft.Row([
        ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=prev_month, tooltip="Mês anterior"),
        month_title_text,
        ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=next_month, tooltip="Próximo mês"),
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    dias = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
    header_days = ft.Row(
        controls=[ft.Text(d, width=60, size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=text_color) for d in dias],
        spacing=5,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    def build_linhas():
        calendar.setfirstweekday(calendar.SUNDAY)
        matriz = calendar.monthcalendar(state["ano"], state["mes"])
        # Garante sempre 6 linhas
        while len(matriz) < 6:
            matriz.append([0]*7)
        linhas = []
        for semana in matriz:
            cells = []
            for dia in semana:
                if dia == 0:
                    cells.append(ft.Container(width=60, height=40))
                else:
                    cells.append(
                        ft.TextButton(
                            text=str(dia),
                            width=60,
                            height=40,
                            style=ft.ButtonStyle(color={"default": text_color}),
                            on_click=lambda e, d=dia: on_day_click(d) if on_day_click else None
                        )
                    )
            linhas.append(ft.Row(controls=cells, spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
        return linhas

    linhas_container = ft.Column(build_linhas(), spacing=8)

    return ft.Container(
        content=ft.Column([
            header,
            header_days,
            linhas_container
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
        width=width,
        height=height,
        alignment=ft.alignment.center
    )
