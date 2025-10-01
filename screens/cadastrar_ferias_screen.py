import flet as ft
from .base_screen import BaseScreen
import datetime

class CadastrarFeriasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "cadastrar_ferias"

    def get_content(self) -> ft.Control:
        # Função para buscar policial pela matrícula
        def buscar_policial(e):
            valor = matricula.value.strip()
            if valor:
                policial_info = self.app.db.get_policial_by_matricula(valor)
                if policial_info:
                    policial.value = policial_info.get("qra", "")
                    nome.value = policial_info.get("nome", "")
                    # Pega a primeira letra da escala
                    escala = policial_info.get("escala", "")
                    equipe.value = escala[0] if escala else ""
                else:
                    # Limpa os campos se não encontrar o policial
                    policial.value = ""
                    nome.value = ""
                    equipe.value = ""
            else:
                # Limpa os campos se a matrícula estiver vazia
                policial.value = ""
                nome.value = ""
                equipe.value = ""
            e.control.page.update()

        # Busca EXATA por QRA ou Nome ao digitar no campo 'policial'
        def buscar_policial_por_qra_ou_nome(e):
            termo = policial.value.strip()
            if not termo:
                e.control.page.update()
                return
            try:
                query = (
                    """
                    SELECT id, nome, qra, matricula, escala
                    FROM policiais
                    WHERE unidade = 'NUVIG'
                      AND (
                            UPPER(qra) = UPPER(?)
                         OR UPPER(nome) = UPPER(?)
                          )
                    LIMIT 1
                    """
                )
                rows = self.app.db.execute_query(query, (termo, termo))
                if rows:
                    row = rows[0]
                    matricula.value = (row["matricula"] if "matricula" in row.keys() else matricula.value) or matricula.value
                    policial.value = (row["qra"] if "qra" in row.keys() else policial.value) or policial.value
                    nome.value = (row["nome"] if "nome" in row.keys() else nome.value) or nome.value
                    escala = row["escala"] if "escala" in row.keys() else ""
                    equipe.value = escala[0] if escala else equipe.value
            except Exception as err:
                print(f"[Férias] Erro ao buscar por QRA/Nome: {err}")
            e.control.page.update()

        # Função para calcular dias entre duas datas
        def calcular_dias(data_inicio, data_fim):
            if not data_inicio or not data_fim:
                return 0
            try:
                from datetime import datetime
                inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
                fim = datetime.strptime(data_fim, "%d/%m/%Y")
                return (fim - inicio).days + 1  # +1 porque inclui ambos os dias
            except:
                return 0

        total_dias = 0
        # Função para atualizar contador de dias
        def atualizar_contador():
            dias_periodo1 = calcular_dias(data_inicio1.value, data_fim1.value) if data_inicio1.value and data_fim1.value else 0
            dias_periodo2 = calcular_dias(data_inicio2.value, data_fim2.value) if data_inicio2.value and data_fim2.value else 0
            dias_periodo3 = calcular_dias(data_inicio3.value, data_fim3.value) if data_inicio3.value and data_fim3.value else 0
            
            total_dias = dias_periodo1 + dias_periodo2 + dias_periodo3
            
            # Atualizar labels dos períodos
            if dias_periodo1 > 0:
                periodo1_label.value = f"Período 1 ({dias_periodo1} dias)"
                periodo1_label.color = ft.Colors.GREEN if dias_periodo1 <= 30 else ft.Colors.RED
            else:
                periodo1_label.value = "Período 1"
                periodo1_label.color = ft.Colors.BLACK
                
            if dias_periodo2 > 0:
                periodo2_label.value = f"Período 2 ({dias_periodo2} dias)"
                periodo2_label.color = ft.Colors.GREEN if dias_periodo2 <= 30 else ft.Colors.RED
            else:
                periodo2_label.value = "Período 2 (Opcional)"
                periodo2_label.color = ft.Colors.GREY
                
            if dias_periodo3 > 0:
                periodo3_label.value = f"Período 3 ({dias_periodo3} dias)"
                periodo3_label.color = ft.Colors.GREEN if dias_periodo3 <= 30 else ft.Colors.RED
            else:
                periodo3_label.value = "Período 3 (Opcional)"
                periodo3_label.color = ft.Colors.GREY
            
            # Atualizar contador total
            contador_total.value = f"Total: {total_dias} de 30 dias"
            if total_dias == 30:
                contador_total.color = ft.Colors.GREEN
            elif total_dias > 30:
                contador_total.color = ft.Colors.RED
            else:
                contador_total.color = ft.Colors.BLACK
            
            # Atualizar a interface
            try:
                periodo1_label.update()
                periodo2_label.update()
                periodo3_label.update()
                contador_total.update()
            except:
                pass

        # Função para mostrar AlertDialog de erro de data
        def mostrar_erro_data(page, mensagem):
            def fechar_dialogo(e):
                page.close(dialogo_erro)
            
            dialogo_erro = ft.AlertDialog(
                modal=True,
                title=ft.Text("Data Inválida", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                content=ft.Text(mensagem, size=14),
                actions=[
                    ft.TextButton("Entendi", on_click=fechar_dialogo)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            page.open(dialogo_erro)

        # Função para mostrar AlertDialog de erro de período
        def mostrar_erro_periodo(page):
            def fechar_dialogo(e):
                page.close(dialogo_erro)
            
            dialogo_erro = ft.AlertDialog(
                modal=True,
                title=ft.Text("Período de Férias Inválido", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    "O total de dias de férias deve ser exatamente 30 dias.\n\n"
                    "Você pode dividir em:\n"
                    "• 1 período de 30 dias\n"
                    "• 2 períodos de 15 dias cada\n"
                    "• 3 períodos de 10 dias cada\n",
                    size=14
                ),
                actions=[
                    ft.TextButton("Entendi", on_click=fechar_dialogo)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            page.open(dialogo_erro)

        # Função para verificar conflitos de datas entre policiais da mesma equipe
        def verificar_conflitos_ferias(policial_id, equipe, periodos_novos):
            """
            Verifica se há conflitos de datas entre o policial atual e outros da mesma equipe
            
            Args:
                policial_id: ID do policial atual
                equipe: Primeira letra da escala (equipe)
                periodos_novos: Lista de tuplas (inicio, fim) dos períodos a serem cadastrados
            
            Returns:
                Lista de conflitos encontrados, cada conflito contém:
                - policial_nome: Nome do policial em conflito
                - periodo_conflito: Período que está em conflito
                - data_inicio_conflito: Data início do conflito
                - data_fim_conflito: Data fim do conflito
            """
            conflitos = []
            
            try:
                # Buscar todos os policiais da mesma equipe (primeira letra da escala)
                query_policiais_equipe = """
                    SELECT p.id, p.qra, p.escala 
                    FROM policiais p 
                    WHERE SUBSTR(p.escala, 1, 1) = ? AND p.id != ?
                """
                policiais_equipe = self.app.db.execute_query(query_policiais_equipe, (equipe, policial_id))
                
                if not policiais_equipe:
                    return conflitos
                
                # Para cada policial da equipe, verificar suas férias
                for policial in policiais_equipe:
                    policial_id_conflito = policial["id"] if hasattr(policial, "keys") else policial[0]
                    policial_qra = policial["qra"] if hasattr(policial, "keys") else policial[1]
                    
                    # Buscar férias deste policial
                    query_ferias = """
                        SELECT inicio1, fim1, inicio2, fim2, inicio3, fim3 
                        FROM ferias 
                        WHERE policial_id = ?
                    """
                    ferias_policial = self.app.db.execute_query(query_ferias, (policial_id_conflito,))
                    
                    # Verificar cada período de férias deste policial
                    for ferias in ferias_policial:
                        # Verificar período 1
                        if ferias["inicio1"] and ferias["fim1"]:
                            conflito = verificar_conflito_periodo(
                                periodos_novos, 
                                ferias["inicio1"], 
                                ferias["fim1"], 
                                policial_qra, 
                                "Período 1"
                            )
                            if conflito:
                                conflitos.append(conflito)
                        
                        # Verificar período 2
                        if ferias["inicio2"] and ferias["fim2"]:
                            conflito = verificar_conflito_periodo(
                                periodos_novos, 
                                ferias["inicio2"], 
                                ferias["fim2"], 
                                policial_qra, 
                                "Período 2"
                            )
                            if conflito:
                                conflitos.append(conflito)
                        
                        # Verificar período 3
                        if ferias["inicio3"] and ferias["fim3"]:
                            conflito = verificar_conflito_periodo(
                                periodos_novos, 
                                ferias["inicio3"], 
                                ferias["fim3"], 
                                policial_qra, 
                                "Período 3"
                            )
                            if conflito:
                                conflitos.append(conflito)
                
                return conflitos
                
            except Exception as e:
                print(f"Erro ao verificar conflitos: {e}")
                return conflitos

        def verificar_conflito_periodo(periodos_novos, inicio_existente, fim_existente, policial_qra, periodo_nome):
            """
            Verifica se algum dos períodos novos conflita com um período existente
            
            Args:
                periodos_novos: Lista de tuplas (inicio, fim) dos períodos a serem cadastrados
                inicio_existente: Data início do período existente (formato YYYY-MM-DD)
                fim_existente: Data fim do período existente (formato YYYY-MM-DD)
                policial_qra: QRA do policial que tem o período existente
                periodo_nome: Nome do período (ex: "Período 1")
            
            Returns:
                Dicionário com informações do conflito ou None se não houver conflito
            """
            try:
                from datetime import datetime
                
                # Converter datas existentes para datetime
                inicio_existente_dt = datetime.strptime(inicio_existente, "%Y-%m-%d")
                fim_existente_dt = datetime.strptime(fim_existente, "%Y-%m-%d")
                
                # Verificar cada período novo
                for i, (inicio_novo, fim_novo) in enumerate(periodos_novos, 1):
                    if not inicio_novo or not fim_novo:
                        continue
                    
                    # Converter datas novas para datetime
                    inicio_novo_dt = datetime.strptime(inicio_novo, "%Y-%m-%d")
                    fim_novo_dt = datetime.strptime(fim_novo, "%Y-%m-%d")
                    
                    # Verificar se há sobreposição de datas
                    if not (fim_novo_dt < inicio_existente_dt or inicio_novo_dt > fim_existente_dt):
                        # Há conflito - calcular período de conflito
                        data_inicio_conflito = max(inicio_novo_dt, inicio_existente_dt)
                        data_fim_conflito = min(fim_novo_dt, fim_existente_dt)
                        
                        return {
                            "policial_nome": policial_qra,
                            "periodo_conflito": f"{periodo_nome} do policial {policial_qra}",
                            "data_inicio_conflito": data_inicio_conflito.strftime("%d/%m/%Y"),
                            "data_fim_conflito": data_fim_conflito.strftime("%d/%m/%Y"),
                            "periodo_novo": f"Período {i}",
                            "periodo_existente": periodo_nome
                        }
                
                return None
                
            except Exception as e:
                print(f"Erro ao verificar conflito de período: {e}")
                return None

        # Função para mostrar diálogo de conflito de datas
        def mostrar_dialogo_conflito(page, conflitos, callback_confirmar):
            def fechar_dialogo(e):
                page.close(dialogo_conflito)
            
            def confirmar_gravacao(e):
                page.close(dialogo_conflito)
                callback_confirmar()
            
            # Construir mensagem de conflito
            mensagem_conflito = "ATENÇÃO: Conflito de datas detectado!\n\n"
            mensagem_conflito += "Os períodos de férias informados conflitam com férias de outros policiais da mesma equipe:\n\n"
            
            for conflito in conflitos:
                mensagem_conflito += f"• {conflito['policial_nome']} ({conflito['periodo_existente']})\n"
                mensagem_conflito += f"  Conflito: {conflito['data_inicio_conflito']} até {conflito['data_fim_conflito']}\n\n"
            
            mensagem_conflito += "Deseja mesmo assim cadastrar as férias?"
            
            dialogo_conflito = ft.AlertDialog(
                modal=True,
                title=ft.Text("Conflito de Datas", color=ft.Colors.ORANGE, weight=ft.FontWeight.BOLD),
                content=ft.Text(mensagem_conflito, size=14),
                actions=[
                    ft.TextButton("Cancelar", on_click=fechar_dialogo),
                    ft.TextButton("Confirmar", on_click=confirmar_gravacao, style=ft.ButtonStyle(color=ft.Colors.RED))
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            page.open(dialogo_conflito)

        # Função para validar se data fim é maior que data início
        def validar_ordem_datas(data_inicio, data_fim):
            if not data_inicio or not data_fim:
                return True
            try:
                from datetime import datetime
                inicio = datetime.strptime(data_inicio, "%d/%m/%Y")
                fim = datetime.strptime(data_fim, "%d/%m/%Y")
                return fim >= inicio
            except:
                return False

        # Função para validar período
        def validar_periodo(periodo_num, data_inicio, data_fim, page):
            if data_inicio and data_fim:
                if not validar_ordem_datas(data_inicio, data_fim):
                    mostrar_erro_data(page, f"No período {periodo_num}, a data fim deve ser igual ou posterior à data início.")
                    return False
                
                dias = calcular_dias(data_inicio, data_fim)
                if dias > 30:
                    mostrar_erro_data(page, f"No período {periodo_num}, o máximo são 30 dias por período. Você selecionou {dias} dias.")
                    return False
            return True

        # Campos do formulário
        matricula = ft.TextField(
            label="Matrícula", 
            width=200,
            max_length=8,
            bgcolor=ft.Colors.WHITE,
            #input_filter=ft.NumbersOnlyInputFilter(),
            on_change=buscar_policial
        )
        policial = ft.TextField(
            label="QRA",
            width=200,
            bgcolor=ft.Colors.WHITE,
            read_only=False,
        )
        nome = ft.TextField(
            label="Nome", 
            width=200, 
            read_only=True,
            disabled=True,
            bgcolor=ft.Colors.GREY_100,
            border_color=ft.Colors.GREY_400,
            text_style=ft.TextStyle(color=ft.Colors.GREY_700)
        )
        equipe = ft.TextField(
            label="Equipe", 
            width=200, 
            read_only=True,
            disabled=True,
            bgcolor=ft.Colors.GREY_100,
            border_color=ft.Colors.GREY_400,
            text_style=ft.TextStyle(color=ft.Colors.GREY_700)
        )
        
        # Campo para período aquisitivo
        periodo_aquisitivo = ft.TextField(
            label="Período Aquisitivo (ex: 2024/2025)",
            width=200,
            bgcolor=ft.Colors.WHITE,
            hint_text="aaaa/aaaa",
            #input_filter=ft.NumbersOnlyInputFilter(),
            #max_length=4
        )

        # Campos de data
        data_inicio1 = ft.TextField(label="Data Início",
                                    width=200,
                                    bgcolor=ft.Colors.WHITE,
                                    hint_text="dd/mm/aaaa")
        data_fim1 = ft.TextField(label="Data Fim",
                                 width=200,
                                 bgcolor=ft.Colors.WHITE,
                                 hint_text="dd/mm/aaaa")
        data_inicio2 = ft.TextField(label="Data Início",
                                    width=200,
                                    bgcolor=ft.Colors.WHITE,
                                    hint_text="dd/mm/aaaa")
        data_fim2 = ft.TextField(label="Data Fim",
                                 width=200,
                                 bgcolor=ft.Colors.WHITE,
                                 hint_text="dd/mm/aaaa")
        data_inicio3 = ft.TextField(label="Data Início",
                                    width=200,
                                    bgcolor=ft.Colors.WHITE,
                                    hint_text="dd/mm/aaaa")
        data_fim3 = ft.TextField(label="Data Fim",
                                 bgcolor=ft.Colors.WHITE,
                                 width=200,
                                 hint_text="dd/mm/aaaa")

        # Configuração de localização para português do Brasil
        def configure_locale(page):
            if hasattr(page, 'locale_configuration') and page.locale_configuration is None:
                page.locale_configuration = ft.LocaleConfiguration(
                    supported_locales=[
                        ft.Locale("pt", "BR"),
                        ft.Locale("en", "US")
                    ],
                    current_locale=ft.Locale("pt", "BR")
                )

        # DatePickers para Período 1
        datepicker_inicio1 = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )

        def on_inicio1_change(e):
            if datepicker_inicio1.value:
                data_inicio1.value = datepicker_inicio1.value.strftime("%d/%m/%Y")
                if not validar_periodo(1, data_inicio1.value, data_fim1.value, e.control.page):
                    data_inicio1.value = ""
                on_change_inicio1(e)
                atualizar_contador()
                e.control.page.update()

        datepicker_inicio1.on_change = on_inicio1_change

        datepicker_fim1 = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )

        def on_fim1_change(e):
            if datepicker_fim1.value:
                data_fim1.value = datepicker_fim1.value.strftime("%d/%m/%Y")
                if not validar_periodo(1, data_inicio1.value, data_fim1.value, e.control.page):
                    data_fim1.value = ""
                on_change_fim1(e)
                atualizar_contador()
                e.control.page.update()

        datepicker_fim1.on_change = on_fim1_change

        # DatePickers para Período 2
        datepicker_inicio2 = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )

        def on_inicio2_change(e):
            if datepicker_inicio2.value:
                data_inicio2.value = datepicker_inicio2.value.strftime("%d/%m/%Y")
                if not validar_periodo(2, data_inicio2.value, data_fim2.value, e.control.page):
                    data_inicio2.value = ""
                on_change_inicio2(e)
                atualizar_contador()
                e.control.page.update()

        datepicker_inicio2.on_change = on_inicio2_change

        datepicker_fim2 = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )

        def on_fim2_change(e):
            if datepicker_fim2.value:
                data_fim2.value = datepicker_fim2.value.strftime("%d/%m/%Y")
                if not validar_periodo(2, data_inicio2.value, data_fim2.value, e.control.page):
                    data_fim2.value = ""
                on_change_fim2(e)
                atualizar_contador()
                e.control.page.update()

        datepicker_fim2.on_change = on_fim2_change

        # DatePickers para Período 3
        datepicker_inicio3 = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )

        def on_inicio3_change(e):
            if datepicker_inicio3.value:
                data_inicio3.value = datepicker_inicio3.value.strftime("%d/%m/%Y")
                if not validar_periodo(3, data_inicio3.value, data_fim3.value, e.control.page):
                    data_inicio3.value = ""
                on_change_inicio3(e)
                atualizar_contador()
                e.control.page.update()

        datepicker_inicio3.on_change = on_inicio3_change

        datepicker_fim3 = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )

        def on_fim3_change(e):
            if datepicker_fim3.value:
                data_fim3.value = datepicker_fim3.value.strftime("%d/%m/%Y")
                if not validar_periodo(3, data_inicio3.value, data_fim3.value, e.control.page):
                    data_fim3.value = ""
                on_change_fim3(e)
                atualizar_contador()
                e.control.page.update()

        datepicker_fim3.on_change = on_fim3_change

        # Função para abrir DatePicker
        def open_date_picker(picker, page):
            configure_locale(page)
            if picker not in page.overlay:
                page.overlay.append(picker)
                page.update()
            page.open(picker)

        # Botões para DatePickers
        btn_inicio1 = ft.ElevatedButton(
            text="Início P1",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
            ),
            width=100,
            on_click=lambda e: open_date_picker(datepicker_inicio1, e.control.page)
        )

        btn_fim1 = ft.ElevatedButton(
            text="Fim P1",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
            ),
            width=100,
            on_click=lambda e: open_date_picker(datepicker_fim1, e.control.page)
        )

        btn_inicio2 = ft.ElevatedButton(
            text="Início P2",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
            ),
            width=100,
            on_click=lambda e: open_date_picker(datepicker_inicio2, e.control.page)
        )

        btn_fim2 = ft.ElevatedButton(
            text="Fim P2",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
            ),
            width=100,
            on_click=lambda e: open_date_picker(datepicker_fim2, e.control.page)
        )

        btn_inicio3 = ft.ElevatedButton(
            text="Início P3",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
            ),
            width=100,
            on_click=lambda e: open_date_picker(datepicker_inicio3, e.control.page)
        )

        btn_fim3 = ft.ElevatedButton(
            text="Fim P3",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
            ),
            width=100,
            on_click=lambda e: open_date_picker(datepicker_fim3, e.control.page)
        )


        def mask_date(field):
            valor = ''.join(c for c in field.value if c.isdigit())
            novo = ''
            if len(valor) > 0:
                novo += valor[:2]
            if len(valor) > 2:
                novo += '/' + valor[2:4]
            if len(valor) > 4:
                novo += '/' + valor[4:8]
            field.value = novo

        def on_change_inicio1(e):
            mask_date(data_inicio1)
            atualizar_contador()
            dias_periodo1 = calcular_dias(data_inicio1.value, data_fim1.value)
            if len(str(data_inicio1.value)) == 10 and len(str(data_fim1.value)) == 10 and dias_periodo1 < 30:
                data_inicio2.disabled = False
                data_fim2.disabled = False
                btn_inicio2.disabled = False
                btn_fim2.disabled = False
            else:
                data_inicio2.value = ""
                data_fim2.value = ""
                data_inicio3.value = ""
                data_fim3.value = ""
                data_inicio2.disabled = True
                data_fim2.disabled = True
                btn_inicio2.disabled = True
                btn_fim2.disabled = True
                data_inicio3.disabled = True
                data_fim3.disabled = True
                btn_inicio3.disabled = True
                btn_fim3.disabled = True

            contador_total.update()
            e.control.page.update()

        def on_change_inicio2(e):
            mask_date(data_inicio2)
            atualizar_contador()
            dias_periodo1 = calcular_dias(data_inicio1.value, data_fim1.value)
            dias_periodo2 = calcular_dias(data_inicio2.value, data_fim2.value)
            dias_periodo12 = dias_periodo1 + dias_periodo2
            if (len(str(data_inicio1.value)) == 10 and len(str(data_fim1.value)) == 10 and dias_periodo12 < 30 and
                    len(str(data_inicio2.value)) == 10 and len(str(data_fim2.value)) == 10):
                data_inicio3.disabled = False
                data_fim3.disabled = False
                btn_inicio3.disabled = False
                btn_fim3.disabled = False
            else:
                data_inicio3.value = ""
                data_fim3.value = ""
                data_inicio3.disabled = True
                data_fim3.disabled = True
                btn_inicio3.disabled = True
                btn_fim3.disabled = True
            contador_total.update()
            e.control.page.update()

        def on_change_inicio3(e):
            mask_date(data_inicio3)
            atualizar_contador()
            contador_total.update()
            e.control.page.update()


        def on_change_fim1(e):
            mask_date(data_fim1)
            atualizar_contador()
            dias_periodo1 = calcular_dias(data_inicio1.value, data_fim1.value)
            if len(str(data_inicio1.value)) == 10 and len(str(data_fim1.value)) == 10 and dias_periodo1 < 30:
                data_inicio2.disabled = False
                data_fim2.disabled = False
                btn_inicio2.disabled = False
                btn_fim2.disabled = False

            else:
                data_inicio2.value = ""
                data_fim2.value = ""
                data_inicio3.value = ""
                data_fim3.value = ""
                data_inicio2.disabled = True
                data_fim2.disabled = True
                btn_inicio2.disabled = True
                btn_fim2.disabled = True
                data_inicio3.disabled = True
                data_fim3.disabled = True
                btn_inicio3.disabled = True
                btn_fim3.disabled = True

            contador_total.update()
            e.control.page.update()

        def on_change_fim2(e):
            mask_date(data_fim2)
            atualizar_contador()
            dias_periodo1 = calcular_dias(data_inicio1.value, data_fim1.value)
            dias_periodo2 = calcular_dias(data_inicio2.value, data_fim2.value)
            dias_periodo12 = dias_periodo1 + dias_periodo2
            if (len(str(data_inicio1.value)) == 10 and len(str(data_fim1.value)) == 10 and dias_periodo12 < 30 and
                    len(str(data_inicio2.value)) == 10 and len(str(data_fim2.value)) == 10):
                data_inicio3.disabled = False
                data_fim3.disabled = False
                btn_inicio3.disabled = False
                btn_fim3.disabled = False
            else:
                data_inicio3.value = ""
                data_fim3.value = ""
                data_inicio3.disabled = True
                data_fim3.disabled = True
                btn_inicio3.disabled = True
                btn_fim3.disabled = True
            contador_total.update()
            e.control.page.update()

        def on_change_fim3(e):
            mask_date(data_fim3)
            atualizar_contador()
            contador_total.update()
            e.control.page.update()

        # Conectar as máscaras aos campos
        data_inicio1.on_change = on_change_inicio1
        data_fim1.on_change = on_change_fim1
        data_inicio2.on_change = on_change_inicio2
        data_fim2.on_change = on_change_fim2
        data_inicio3.on_change = on_change_inicio3
        data_fim3.on_change = on_change_fim3


        data_inicio2.disabled = True
        data_fim2.disabled = True
        data_inicio3.disabled = True
        data_fim3.disabled = True
        btn_inicio2.disabled = True
        btn_inicio3.disabled = True
        btn_fim2.disabled = True
        btn_fim3.disabled = True

        # Habilitar busca por QRA/Nome ao digitar no campo 'policial'
        policial.on_change = buscar_policial_por_qra_ou_nome



        # Labels dos períodos e contador
        periodo1_label = ft.Text("Período 1", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
        periodo2_label = ft.Text("Período 2 (Opcional)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY,)
        periodo3_label = ft.Text("Período 3 (Opcional)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY,)
        contador_total = ft.Text("Total: 0 de 30 dias", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE,width=matricula.width)

        


        form_grid = ft.Column([
            ft.Text("Dados do Policial", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Row([
                matricula, policial, periodo_aquisitivo
            ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                nome, equipe, contador_total
            ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            # ft.Row([
            #     periodo_aquisitivo
            # ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            
            # ft.Container(height=20),
            # contador_total,
            ft.Container(height=10),
            
            periodo1_label,
            ft.Row([
                btn_inicio1, data_inicio1, btn_fim1, data_fim1
            ], spacing=16, alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=15),
            periodo2_label,
            ft.Row([
                btn_inicio2, data_inicio2, btn_fim2, data_fim2
            ], spacing=16, alignment=ft.MainAxisAlignment.CENTER),
            
            ft.Container(height=15),
            periodo3_label,
            ft.Row([
                btn_inicio3, data_inicio3, btn_fim3, data_fim3
            ], spacing=16, alignment=ft.MainAxisAlignment.CENTER),
            
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # Função para mostrar AlertDialog de sucesso/erro
        def mostrar_resultado_gravacao(page, sucesso, mensagem):
            def fechar_dialogo(e):
                page.close(dialogo_resultado)
            
            cor_titulo = ft.Colors.GREEN if sucesso else ft.Colors.RED
            titulo = "Sucesso!" if sucesso else "Erro!"
            
            dialogo_resultado = ft.AlertDialog(
                modal=True,
                title=ft.Text(titulo, color=cor_titulo, weight=ft.FontWeight.BOLD),
                content=ft.Text(mensagem, size=14),
                actions=[
                    ft.TextButton("OK", on_click=fechar_dialogo)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            page.open(dialogo_resultado)

        # Função para gravar férias
        def gravar_ferias(e):
            # Validar se todos os campos obrigatórios estão preenchidos
            if not matricula.value.strip():
                mostrar_resultado_gravacao(e.control.page, False, "Matrícula é obrigatória!")
                return
            
            if not periodo_aquisitivo.value.strip():
                mostrar_resultado_gravacao(e.control.page, False, "Período aquisitivo é obrigatório!")
                return
            
            if not data_inicio1.value.strip() or not data_fim1.value.strip():
                mostrar_resultado_gravacao(e.control.page, False, "Período 1 é obrigatório!")
                return
            
            # Validar se o total é exatamente 30 dias
            dias_periodo1 = calcular_dias(data_inicio1.value, data_fim1.value)
            dias_periodo2 = calcular_dias(data_inicio2.value, data_fim2.value) if data_inicio2.value and data_fim2.value else 0
            dias_periodo3 = calcular_dias(data_inicio3.value, data_fim3.value) if data_inicio3.value and data_fim3.value else 0
            total_dias = dias_periodo1 + dias_periodo2 + dias_periodo3

            if total_dias != 30:
                mostrar_erro_periodo(e.control.page)
                return
            
            try:
                # Buscar o policial pela matrícula usando o mesmo método que funciona na busca
                policial_info = self.app.db.get_policial_by_matricula(matricula.value.strip())
                
                if not policial_info:
                    mostrar_resultado_gravacao(e.control.page, False, "Policial não encontrado!")
                    return
                
                policial_id = policial_info.get("id")
                
                # Converter datas para formato SQL
                from datetime import datetime
                def converter_data(data_str):
                    if data_str:
                        return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                    return None
                
                inicio1 = converter_data(data_inicio1.value)
                fim1 = converter_data(data_fim1.value)
                inicio2 = converter_data(data_inicio2.value)
                fim2 = converter_data(data_fim2.value)
                inicio3 = converter_data(data_inicio3.value)
                fim3 = converter_data(data_fim3.value)
                
                # Preparar períodos para validação de conflitos
                periodos_novos = []
                if inicio1 and fim1:
                    periodos_novos.append((inicio1, fim1))
                if inicio2 and fim2:
                    periodos_novos.append((inicio2, fim2))
                if inicio3 and fim3:
                    periodos_novos.append((inicio3, fim3))
                
                # Verificar conflitos com outros policiais da mesma equipe
                conflitos = verificar_conflitos_ferias(policial_id, equipe.value, periodos_novos)
                
                if conflitos:
                    # Mostrar diálogo de conflito e aguardar confirmação
                    def confirmar_gravacao_com_conflito():
                        executar_gravacao(e.control.page)
                    
                    mostrar_dialogo_conflito(e.control.page, conflitos, confirmar_gravacao_com_conflito)
                else:
                    # Não há conflitos, gravar diretamente
                    executar_gravacao(e.control.page)
                    
            except ValueError as ve:
                mostrar_resultado_gravacao(e.control.page, False, f"Formato de data inválido: {str(ve)}")
            except Exception as ex:
                mostrar_resultado_gravacao(e.control.page, False, f"Erro inesperado: {str(ex)}")

        # Função auxiliar para executar a gravação das férias
        def executar_gravacao(page_ref):
            try:
                # Buscar o policial pela matrícula usando o mesmo método que funciona na busca
                policial_info = self.app.db.get_policial_by_matricula(matricula.value.strip())
                
                if not policial_info:
                    mostrar_resultado_gravacao(page_ref, False, "Policial não encontrado!")
                    return
                
                policial_id = policial_info.get("id")
                
                # Converter datas para formato SQL
                from datetime import datetime
                def converter_data(data_str):
                    if data_str:
                        return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                    return None
                
                inicio1 = converter_data(data_inicio1.value)
                fim1 = converter_data(data_fim1.value)
                inicio2 = converter_data(data_inicio2.value)
                fim2 = converter_data(data_fim2.value)
                inicio3 = converter_data(data_inicio3.value)
                fim3 = converter_data(data_fim3.value)
                
                # Inserir na tabela ferias
                query_insert = """
                    INSERT INTO ferias (policial_id, periodo_aquisitivo, inicio1, fim1, inicio2, fim2, inicio3, fim3)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                success = self.app.db.execute_command(
                    query_insert, 
                    (policial_id, periodo_aquisitivo.value, inicio1, fim1, inicio2, fim2, inicio3, fim3)
                )
                
                if success:
                    dias_periodo1 = calcular_dias(data_inicio1.value, data_fim1.value)
                    dias_periodo2 = calcular_dias(data_inicio2.value, data_fim2.value) if data_inicio2.value and data_fim2.value else 0
                    dias_periodo3 = calcular_dias(data_inicio3.value, data_fim3.value) if data_inicio3.value and data_fim3.value else 0
                    total_dias = dias_periodo1 + dias_periodo2 + dias_periodo3
                    
                    periodos_texto = f"Período 1: {data_inicio1.value} a {data_fim1.value} ({dias_periodo1} dias)"
                    if dias_periodo2 > 0:
                        periodos_texto += f"\nPeríodo 2: {data_inicio2.value} a {data_fim2.value} ({dias_periodo2} dias)"
                    if dias_periodo3 > 0:
                        periodos_texto += f"\nPeríodo 3: {data_inicio3.value} a {data_fim3.value} ({dias_periodo3} dias)"
                    
                    mostrar_resultado_gravacao(
                        page_ref, 
                        True, 
                        f"Férias gravadas com sucesso!\n\n"
                        f"Policial: {nome.value}\n"
                        f"Período Aquisitivo: {periodo_aquisitivo.value}\n"
                        f"Total: {total_dias} dias\n\n"
                        f"{periodos_texto}"
                    )
                    # Limpar o formulário após sucesso
                    limpar_formulario(page_ref)
                else:
                    mostrar_resultado_gravacao(page_ref, False, "Erro ao gravar as férias!")
                    
            except ValueError as ve:
                mostrar_resultado_gravacao(page_ref, False, f"Formato de data inválido: {str(ve)}")
            except Exception as ex:
                mostrar_resultado_gravacao(page_ref, False, f"Erro inesperado: {str(ex)}")

        # Função para limpar o formulário
        def limpar_formulario(e):
            # Limpar todos os campos
            matricula.value = ""
            policial.value = ""
            nome.value = ""
            equipe.value = ""
            periodo_aquisitivo.value = ""
            data_inicio1.value = ""
            data_fim1.value = ""
            data_inicio2.value = ""
            data_fim2.value = ""
            data_inicio3.value = ""
            data_fim3.value = ""
            
            # Atualizar contador
            atualizar_contador()
            
            # Atualizar os campos na interface
            matricula.update()
            policial.update()
            nome.update()
            equipe.update()
            periodo_aquisitivo.update()
            data_inicio1.update()
            data_fim1.update()
            data_inicio2.update()
            data_fim2.update()
            data_inicio3.update()
            data_fim3.update()

        # Botões
        btn_gravar = ft.ElevatedButton(
            text="Gravar",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.GREEN)),
            icon=ft.Icons.SAVE,
            width=150,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.GREEN,
            on_click=gravar_ferias
        )
        btn_limpar = ft.ElevatedButton(
            text="Limpar",
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.RED)),
            icon=ft.Icons.DELETE,
            width=btn_gravar.width,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.RED,
            on_click=limpar_formulario
        )
        btn_row = ft.Row([
            btn_gravar,
            btn_limpar
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            ft.Text("Cadastrar Férias", size=28, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20),
            form_grid,
            ft.Container(height=30),
            btn_row
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
