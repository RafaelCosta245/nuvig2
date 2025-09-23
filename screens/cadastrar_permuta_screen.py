import flet as ft
from .base_screen import BaseScreen

class CadastrarPermutaScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "cadastrar_permuta"

    def get_content(self) -> ft.Control:
        # Função para buscar policial pela matrícula
        def buscar_policial_solicitante(e):
            valor = matricula_solicitante.value.strip()
            if valor:
                policial_info = self.app.db.get_policial_by_matricula(valor)
                if policial_info:
                    policial_solicitante.value = policial_info.get("qra", "")
                    nome_solicitante.value = policial_info.get("nome", "")
                    # Pega a primeira letra da escala
                    escala = policial_info.get("escala", "")
                    equipe_solicitante.value = escala[0] if escala else ""
                else:
                    # Limpa os campos se não encontrar o policial
                    policial_solicitante.value = ""
                    nome_solicitante.value = ""
                    equipe_solicitante.value = ""
            else:
                # Limpa os campos se a matrícula estiver vazia
                policial_solicitante.value = ""
                nome_solicitante.value = ""
                equipe_solicitante.value = ""
            e.control.page.update()

        def buscar_policial_permutado(e):
            valor = matricula_permutado.value.strip()
            if valor:
                policial_info = self.app.db.get_policial_by_matricula(valor)
                if policial_info:
                    policial_permutado.value = policial_info.get("qra", "")
                    nome_permutado.value = policial_info.get("nome", "")
                    # Pega a primeira letra da escala
                    escala = policial_info.get("escala", "")
                    equipe_permutado.value = escala[0] if escala else ""
                else:
                    # Limpa os campos se não encontrar o policial
                    policial_permutado.value = ""
                    nome_permutado.value = ""
                    equipe_permutado.value = ""
            else:
                # Limpa os campos se a matrícula estiver vazia
                policial_permutado.value = ""
                nome_permutado.value = ""
                equipe_permutado.value = ""
            e.control.page.update()

        # Busca EXATA por QRA ou Nome para o SOLICITANTE
        def buscar_por_qra_ou_nome_solicitante(e):
            termo = policial_solicitante.value.strip()
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
                    matricula_solicitante.value = (row["matricula"] if "matricula" in row.keys() else matricula_solicitante.value) or matricula_solicitante.value
                    policial_solicitante.value = (row["qra"] if "qra" in row.keys() else policial_solicitante.value) or policial_solicitante.value
                    nome_solicitante.value = (row["nome"] if "nome" in row.keys() else nome_solicitante.value) or nome_solicitante.value
                    escala = row["escala"] if "escala" in row.keys() else ""
                    equipe_solicitante.value = escala[0] if escala else equipe_solicitante.value
            except Exception as err:
                print(f"[Permuta] Erro ao buscar solicitante por QRA/Nome: {err}")
            e.control.page.update()

        # Busca EXATA por QRA ou Nome para o PERMUTADO
        def buscar_por_qra_ou_nome_permutado(e):
            termo = policial_permutado.value.strip()
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
                    matricula_permutado.value = (row["matricula"] if "matricula" in row.keys() else matricula_permutado.value) or matricula_permutado.value
                    policial_permutado.value = (row["qra"] if "qra" in row.keys() else policial_permutado.value) or policial_permutado.value
                    nome_permutado.value = (row["nome"] if "nome" in row.keys() else nome_permutado.value) or nome_permutado.value
                    escala = row["escala"] if "escala" in row.keys() else ""
                    equipe_permutado.value = escala[0] if escala else equipe_permutado.value
            except Exception as err:
                print(f"[Permuta] Erro ao buscar permutado por QRA/Nome: {err}")
            e.control.page.update()

        # Função para mostrar AlertDialog de erro de data
        def mostrar_erro_data(page):
            def fechar_dialogo(e):
                page.close(dialogo_erro)
            
            dialogo_erro = ft.AlertDialog(
                modal=True,
                title=ft.Text("Data Inválida", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    "A data 'Permuta Com' deve ser diferente da data 'Permuta De'.\n\n"
                    "Por favor, selecione datas diferentes para a permuta.",
                    size=14
                ),
                actions=[
                    ft.TextButton("Entendi", on_click=fechar_dialogo)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Abrir o diálogo usando page.open()
            page.open(dialogo_erro)

        # Função para mostrar AlertDialog de erro de equipe
        def mostrar_erro_equipe(page, data_selecionada, equipe_calendario, equipe_policial, tipo_policial):
            def fechar_dialogo(e):
                page.close(dialogo_erro)
            
            dialogo_erro = ft.AlertDialog(
                modal=True,
                title=ft.Text("Equipe Incompatível", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    f"A data {data_selecionada} pertence à equipe '{equipe_calendario}', "
                    f"mas o policial {tipo_policial} está na equipe '{equipe_policial}'.\n\n"
                    "Por favor, selecione uma data que pertença à equipe do policial.",
                    size=14
                ),
                actions=[
                    ft.TextButton("Entendi", on_click=fechar_dialogo)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Abrir o diálogo usando page.open()
            page.open(dialogo_erro)

        # Função para mostrar AlertDialog de erro de diferença de dias
        def mostrar_erro_diferenca_dias(page, data1_str, data2_str, dias_diferenca):
            def fechar_dialogo(e):
                page.close(dialogo_erro)
            
            dialogo_erro = ft.AlertDialog(
                modal=True,
                title=ft.Text("Diferença de Dias Excedida", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    f"A diferença entre as datas é de {dias_diferenca} dias, "
                    f"mas o limite máximo é de 30 dias.\n\n"
                    f"Data Permuta De: {data1_str}\n"
                    f"Data Permuta Com: {data2_str}\n\n"
                    "Por favor, selecione uma data dentro do prazo de 30 dias.",
                    size=14
                ),
                actions=[
                    ft.TextButton("Entendi", on_click=fechar_dialogo)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Abrir o diálogo usando page.open()
            page.open(dialogo_erro)

        # Função para mostrar AlertDialog de erro de campos obrigatórios
        def mostrar_erro_campos_obrigatorios(page):
            def fechar_dialogo(e):
                page.close(dialogo_erro)
            
            dialogo_erro = ft.AlertDialog(
                modal=True,
                title=ft.Text("Campos Obrigatórios", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
                content=ft.Text(
                    "Para selecionar as datas, você deve primeiro:\n\n"
                    "1. Preencher as matrículas dos policiais\n"
                    "2. Aguardar o sistema preencher automaticamente os campos QRA, Nome e Equipe\n\n"
                    "Por favor, preencha as matrículas primeiro.",
                    size=14
                ),
                actions=[
                    ft.TextButton("Entendi", on_click=fechar_dialogo)
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            # Abrir o diálogo usando page.open()
            page.open(dialogo_erro)

        # Função para validar datas
        def validar_datas(page):
            if data1.value and data2.value:
                try:
                    # Converter as datas para objetos datetime
                    from datetime import datetime
                    data_permuta_de = datetime.strptime(data1.value, "%d/%m/%Y")
                    data_permuta_com = datetime.strptime(data2.value, "%d/%m/%Y")
                    
                    # Verificar se as datas são diferentes
                    if data_permuta_de == data_permuta_com:
                        # Mostrar AlertDialog de erro e limpar data2
                        mostrar_erro_data(page)
                        data2.value = ""
                        data2.update()
                        return False
                    
                    # Verificar se a diferença não excede 30 dias
                    diferenca = abs((data_permuta_com - data_permuta_de).days)
                    if diferenca > 30:
                        # Mostrar AlertDialog de erro de diferença de dias
                        mostrar_erro_diferenca_dias(page, data1.value, data2.value, diferenca)
                        data2.value = ""
                        data2.update()
                        return False
                    
                    return True
                except ValueError:
                    # Se houver erro no formato da data
                    self.show_error("Formato de data inválido. Use dd/mm/aaaa")
                    return False
            return True

        # Função para validar campos obrigatórios antes de selecionar datas
        def validar_campos_obrigatorios(page):
            if not matricula_solicitante.value.strip():
                mostrar_erro_campos_obrigatorios(page)
                return False
            
            if not matricula_permutado.value.strip():
                mostrar_erro_campos_obrigatorios(page)
                return False
            
            if not equipe_solicitante.value.strip() or not equipe_permutado.value.strip():
                mostrar_erro_campos_obrigatorios(page)
                return False
            
            return True

        # Função para validar equipe da data
        def validar_equipe_data(page, data_str, equipe_valor, tipo_policial):
            if not equipe_valor.strip():
                return True  # Se não há equipe definida, não validar
            
            try:
                # Converter data de dd/mm/aaaa para aaaa-mm-dd
                from datetime import datetime
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                data_sql = data_obj.strftime("%Y-%m-%d")
                
                # Buscar a equipe da data na tabela calendário
                query = "SELECT equipe FROM calendario WHERE data = ?"
                result = self.app.db.execute_query(query, (data_sql,))
                
                if result and len(result) > 0:
                    # Obter a equipe da data no calendário
                    equipe_calendario = result[0]["equipe"] if hasattr(result[0], "keys") else result[0][0]
                    equipe_policial = equipe_valor.strip()
                    
                    # Verificar se as equipes são iguais
                    if equipe_calendario != equipe_policial:
                        # Mostrar erro de equipe incompatível
                        mostrar_erro_equipe(page, data_str, equipe_calendario, equipe_policial, tipo_policial)
                        if tipo_policial == "solicitante":
                            data1.value = ""
                            data1.update()
                        else:
                            data2.value = ""
                            data2.update()
                        return False
                
                return True
            except Exception as e:
                self.show_error(f"Erro ao validar equipe da data: {str(e)}")
                return False

        # Campos do formulário - Policial Solicitante
        matricula_solicitante = ft.TextField(
            label="Matrícula Solicitante",
            width=200,
            max_length=8,
            input_filter=ft.NumbersOnlyInputFilter(), 
            on_change=buscar_policial_solicitante
        )
        policial_solicitante = ft.TextField(
            label="QRA Solicitante",
            width=200,
            read_only=False,
        )
        nome_solicitante = ft.TextField(
            label="Nome Solicitante", 
            width=200, 
            read_only=True,
            disabled=True,
            bgcolor=ft.Colors.GREY_100,
            border_color=ft.Colors.GREY_400,
            text_style=ft.TextStyle(color=ft.Colors.GREY_700)
        )
        equipe_solicitante = ft.TextField(
            label="Equipe Solicitante", 
            width=200, 
            read_only=True,
            disabled=True,
            bgcolor=ft.Colors.GREY_100,
            border_color=ft.Colors.GREY_400,
            text_style=ft.TextStyle(color=ft.Colors.GREY_700)
        )

        # Campos do formulário - Policial Permutado
        matricula_permutado = ft.TextField(
            label="Matrícula Permutado", 
            width=200,
            max_length=8,
            input_filter=ft.NumbersOnlyInputFilter(), 
            on_change=buscar_policial_permutado
        )
        policial_permutado = ft.TextField(
            label="QRA Permutado",
            width=200,
            read_only=False,
        )
        nome_permutado = ft.TextField(
            label="Nome Permutado", 
            width=200, 
            read_only=True,
            disabled=True,
            bgcolor=ft.Colors.GREY_100,
            border_color=ft.Colors.GREY_400,
            text_style=ft.TextStyle(color=ft.Colors.GREY_700)
        )
        equipe_permutado = ft.TextField(
            label="Equipe Permutado", 
            width=200, 
            read_only=True,
            disabled=True,
            bgcolor=ft.Colors.GREY_100,
            border_color=ft.Colors.GREY_400,
            text_style=ft.TextStyle(color=ft.Colors.GREY_700)
        )

        # Campos de data
        data1 = ft.TextField(label="Permuta De", width=200, hint_text="dd/mm/aaaa")
        data2 = ft.TextField(label="Permuta Com", width=200, hint_text="dd/mm/aaaa")
        
        # Função para aplicar máscara de data
        def mascara_data1(e):
            valor = ''.join([c for c in data1.value if c.isdigit()])
            novo_valor = ''
            if len(valor) > 0:
                novo_valor += valor[:2]
            if len(valor) > 2:
                novo_valor += '/' + valor[2:4]
            if len(valor) > 4:
                novo_valor += '/' + valor[4:8]
            data1.value = novo_valor
            e.control.page.update()
        
        def mascara_data2(e):
            valor = ''.join([c for c in data2.value if c.isdigit()])
            novo_valor = ''
            if len(valor) > 0:
                novo_valor += valor[:2]
            if len(valor) > 2:
                novo_valor += '/' + valor[2:4]
            if len(valor) > 4:
                novo_valor += '/' + valor[4:8]
            data2.value = novo_valor
            e.control.page.update()
        
        data1.on_change = mascara_data1
        data2.on_change = mascara_data2

        # Ativar busca exata por QRA/Nome ao digitar nos campos
        policial_solicitante.on_change = buscar_por_qra_ou_nome_solicitante
        policial_permutado.on_change = buscar_por_qra_ou_nome_permutado

        import datetime
        
        # Configuração de localização para português do Brasil
        def configure_locale(page):
            if hasattr(page, 'locale_configuration') and page.locale_configuration is None:
                page.locale_configuration = ft.LocaleConfiguration(
                    supported_locales=[
                        ft.Locale("pt", "BR"),  # Português do Brasil
                        ft.Locale("en", "US")   # Inglês como fallback
                    ],
                    current_locale=ft.Locale("pt", "BR")  # Define pt-BR como padrão
                )
        
        # DatePicker para Data Permuta De
        datepicker1 = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )
        def on_date1_change(e):
            if datepicker1.value:
                # Primeiro validar se os campos obrigatórios estão preenchidos
                if not validar_campos_obrigatorios(e.control.page):
                    data1.value = ""
                    data1.update()
                    return
                
                data1.value = datepicker1.value.strftime("%d/%m/%Y")
                data1.cursor_position = len(data1.value)
                # Validar equipe do policial solicitante
                if not validar_equipe_data(e.control.page, data1.value, equipe_solicitante.value, "solicitante"):
                    return
                # Validar datas após mudança da data1
                validar_datas(e.control.page)
                e.control.page.update()
        datepicker1.on_change = on_date1_change
        def open_date_picker1(e):
            page = e.control.page
            # Configura localização antes de abrir o DatePicker
            configure_locale(page)
            if datepicker1 not in page.overlay:
                page.overlay.append(datepicker1)
                page.update()
            page.open(datepicker1)
        btn_data1 = ft.ElevatedButton(
            text="Permuta De",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
            ),
            width=matricula_solicitante.width,
            height=matricula_solicitante.height,
            on_click=open_date_picker1
        )
        
        # DatePicker para Data Permuta Com
        datepicker2 = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
        )
        def on_date2_change(e):
            if datepicker2.value:
                # Primeiro validar se os campos obrigatórios estão preenchidos
                if not validar_campos_obrigatorios(e.control.page):
                    data2.value = ""
                    data2.update()
                    return
                
                data2.value = datepicker2.value.strftime("%d/%m/%Y")
                data2.cursor_position = len(data2.value)
                # Validar equipe do policial permutado
                if not validar_equipe_data(e.control.page, data2.value, equipe_permutado.value, "permutado"):
                    return
                # Validar datas após mudança da data2
                validar_datas(e.control.page)
                e.control.page.update()
        datepicker2.on_change = on_date2_change
        def open_date_picker2(e):
            page = e.control.page
            # Configura localização antes de abrir o DatePicker
            configure_locale(page)
            if datepicker2 not in page.overlay:
                page.overlay.append(datepicker2)
                page.update()
            page.open(datepicker2)
        btn_data2 = ft.ElevatedButton(
            text="Permuta Com",
            icon=ft.Icons.CALENDAR_MONTH,
            color=ft.Colors.BLACK,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
            ),
            width=matricula_solicitante.width,
            height=matricula_solicitante.height,
            on_click=open_date_picker2
        )

        form_grid = ft.Column([
            ft.Text("Policial Solicitante", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Row([
                matricula_solicitante, policial_solicitante
            ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                nome_solicitante, equipe_solicitante
            ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Text("Policial Permutado", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Row([
                matricula_permutado, policial_permutado
            ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                nome_permutado, equipe_permutado
            ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Text("Datas da Permuta", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Row([
                btn_data1, data1
            ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                btn_data2, data2
            ], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

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
            
            # Abrir o diálogo usando page.open()
            page.open(dialogo_resultado)

        # Função para gravar permuta
        def gravar_permuta(e):
            # Validar se todos os campos obrigatórios estão preenchidos
            if not matricula_solicitante.value.strip():
                mostrar_resultado_gravacao(e.control.page, False, "Matrícula do solicitante é obrigatória!")
                return
            
            if not matricula_permutado.value.strip():
                mostrar_resultado_gravacao(e.control.page, False, "Matrícula do permutado é obrigatória!")
                return
            
            if not data1.value.strip():
                mostrar_resultado_gravacao(e.control.page, False, "Data Permuta De é obrigatória!")
                return
            
            if not data2.value.strip():
                mostrar_resultado_gravacao(e.control.page, False, "Data Permuta Com é obrigatória!")
                return
            
            try:
                # Buscar o ID dos policiais pelas matrículas
                query_policial = "SELECT id FROM policiais WHERE matricula = ?"
                
                result_solicitante = self.app.db.execute_query(query_policial, (matricula_solicitante.value.strip(),))
                if not result_solicitante:
                    mostrar_resultado_gravacao(e.control.page, False, "Policial solicitante não encontrado!")
                    return
                
                result_permutado = self.app.db.execute_query(query_policial, (matricula_permutado.value.strip(),))
                if not result_permutado:
                    mostrar_resultado_gravacao(e.control.page, False, "Policial permutado não encontrado!")
                    return
                
                policial_solicitante_id = result_solicitante[0]["id"] if hasattr(result_solicitante[0], "keys") else result_solicitante[0][0]
                policial_permutado_id = result_permutado[0]["id"] if hasattr(result_permutado[0], "keys") else result_permutado[0][0]
                
                # Converter datas para formato SQL (aaaa-mm-dd)
                from datetime import datetime
                data_permuta_de = datetime.strptime(data1.value, "%d/%m/%Y").strftime("%Y-%m-%d")
                data_permuta_com = datetime.strptime(data2.value, "%d/%m/%Y").strftime("%Y-%m-%d")
                
                # Inserir na tabela permutas
                query_insert = """
                    INSERT INTO permutas (solicitante, permutado, data_solicitante, data_permutado)
                    VALUES (?, ?, ?, ?)
                """
                
                success = self.app.db.execute_command(
                    query_insert, 
                    (policial_solicitante_id, policial_permutado_id, data_permuta_de, data_permuta_com)
                )
                
                if success:
                    mostrar_resultado_gravacao(
                        e.control.page, 
                        True, 
                        f"Permuta gravada com sucesso!\n\n"
                        f"Solicitante: {nome_solicitante.value}\n"
                        f"Permutado: {nome_permutado.value}\n"
                        f"Permuta De: {data1.value}\n"
                        f"Permuta Com: {data2.value}"
                    )
                    # Limpar o formulário após sucesso
                    limpar_formulario(e)
                else:
                    mostrar_resultado_gravacao(e.control.page, False, "Erro ao gravar a permuta!")
                    
            except ValueError as ve:
                mostrar_resultado_gravacao(e.control.page, False, f"Formato de data inválido: {str(ve)}")
            except Exception as ex:
                mostrar_resultado_gravacao(e.control.page, False, f"Erro inesperado: {str(ex)}")

        # Função para limpar o formulário
        def limpar_formulario(e):
            # Limpar todos os campos
            matricula_solicitante.value = ""
            policial_solicitante.value = ""
            nome_solicitante.value = ""
            equipe_solicitante.value = ""
            matricula_permutado.value = ""
            policial_permutado.value = ""
            nome_permutado.value = ""
            equipe_permutado.value = ""
            data1.value = ""
            data2.value = ""
            
            # Atualizar os campos na interface
            matricula_solicitante.update()
            policial_solicitante.update()
            nome_solicitante.update()
            equipe_solicitante.update()
            matricula_permutado.update()
            policial_permutado.update()
            nome_permutado.update()
            equipe_permutado.update()
            data1.update()
            data2.update()

        # Botões
        btn_gravar = ft.ElevatedButton(
            text="Gravar",
            width=150,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.GREEN,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.GREEN)),
            icon=ft.Icons.SAVE,
            color=ft.Colors.GREEN,
            on_click=gravar_permuta
        )
        btn_limpar = ft.ElevatedButton(
            text="Limpar",
            width=150,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.RED,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.RED)),
            icon=ft.Icons.DELETE,
            on_click=limpar_formulario
        )
        btn_row = ft.Row([
            btn_gravar,
            btn_limpar
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

        return ft.Column([
            ft.Text("Cadastrar Permuta", size=28, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
            ft.Container(height=20),
            form_grid,
            ft.Container(height=30),
            btn_row
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
