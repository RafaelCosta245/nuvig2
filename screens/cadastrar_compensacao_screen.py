import flet as ft
from .base_screen import BaseScreen

class CadastrarCompensacaoScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "cadastrar_compensacao"

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

		# Nova função: buscar por QRA ou Nome (EXATO) e preencher matrícula, nome e equipe
		def buscar_policial_por_qra_ou_nome(e):
			termo = policial.value.strip()
			if not termo:
				# Não altera automaticamente se o campo for limpo
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
					# Preenche matrícula, QRA (policial), nome e equipe (1ª letra da escala)
					matricula.value = (row["matricula"] if "matricula" in row.keys() else matricula.value) or matricula.value
					policial.value = (row["qra"] if "qra" in row.keys() else policial.value) or policial.value
					nome.value = (row["nome"] if "nome" in row.keys() else nome.value) or nome.value
					escala = row["escala"] if "escala" in row.keys() else ""
					equipe.value = escala[0] if escala else equipe.value
			except Exception as err:
				print(f"[CadastrarCompensacao] Erro ao buscar por QRA/Nome: {err}")
			e.control.page.update()

		# Função para mostrar AlertDialog de erro de data
		def mostrar_erro_data(page):
			def fechar_dialogo(e):
				page.close(dialogo_erro)
			
			dialogo_erro = ft.AlertDialog(
				modal=True,
				title=ft.Text("Data Inválida", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
				content=ft.Text(
					"A data 'A compensar' deve ser maior que a data 'Compensação'.\n\n"
					"Por favor, selecione uma data posterior à data de compensação.",
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
		def mostrar_erro_equipe(page, data_selecionada, equipe_calendario, equipe_policial):
			def fechar_dialogo(e):
				page.close(dialogo_erro)
			
			dialogo_erro = ft.AlertDialog(
				modal=True,
				title=ft.Text("Equipe Incompatível", color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
				content=ft.Text(
					f"A data {data_selecionada} pertence à equipe '{equipe_calendario}', "
					f"mas o policial está na equipe '{equipe_policial}'.\n\n"
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
					f"Data Compensação: {data1_str}\n"
					f"Data A Compensar: {data2_str}\n\n"
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
					"Para selecionar a data 'A compensar', você deve primeiro:\n\n"
					"1. Preencher a matrícula do policial\n"
					"2. Aguardar o sistema preencher automaticamente os campos QRA, Nome e Equipe\n\n"
					"Por favor, preencha a matrícula primeiro.",
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
					data_compensacao = datetime.strptime(data1.value, "%d/%m/%Y")
					data_a_compensar = datetime.strptime(data2.value, "%d/%m/%Y")
					
					# Verificar se data1 é menor que data2
					if data_compensacao >= data_a_compensar:
						# Mostrar AlertDialog de erro e limpar data2
						mostrar_erro_data(page)
						data2.value = ""
						data2.update()
						return False
					
					# Verificar se a diferença não excede 30 dias
					diferenca = (data_a_compensar - data_compensacao).days
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

		# Função para validar campos obrigatórios antes de selecionar data2
		def validar_campos_obrigatorios(page):
			if not matricula.value.strip():
				mostrar_erro_campos_obrigatorios(page)
				return False
			
			if not equipe.value.strip():
				mostrar_erro_campos_obrigatorios(page)
				return False
			
			return True

		# Função para validar equipe da data
		def validar_equipe_data(page, data_str):
			if not equipe.value.strip():
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
					equipe_policial = equipe.value.strip()
					
					# Verificar se as equipes são iguais
					if equipe_calendario != equipe_policial:
						# Mostrar erro de equipe incompatível
						mostrar_erro_equipe(page, data_str, equipe_calendario, equipe_policial)
						data2.value = ""
						data2.update()
						return False
				
				return True
			except Exception as e:
				self.show_error(f"Erro ao validar equipe da data: {str(e)}")
				return False

		# Campos do formulário
		matricula = ft.TextField(
			label="Matrícula", 
			width=200, 
			input_filter=ft.NumbersOnlyInputFilter(), 
			on_change=buscar_policial
		)
		policial = ft.TextField(
			label="QRA",
			width=200,
			read_only=False,
		)
		nome = ft.TextField(
			label="Nome", 
			width=200, 
			read_only=True,
			disabled=True,
		)
		equipe = ft.TextField(
			label="Equipe", 
			width=200, 
			read_only=True,
			disabled=True,
		)
		data1 = ft.TextField(label="Compensação", width=200, hint_text="dd/mm/aaaa")
		data2 = ft.TextField(label="A compensar", width=200, hint_text="dd/mm/aaaa")
		
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

		# Habilitar busca por QRA/Nome ao digitar no campo 'policial'
		policial.on_change = buscar_policial_por_qra_ou_nome

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
		
		# DatePicker para Data de Compensação
		datepicker1 = ft.DatePicker(
			first_date=datetime.datetime(2020, 1, 1),
			last_date=datetime.datetime(2030, 12, 31),
		)
		def on_date1_change(e):
			if datepicker1.value:
				data1.value = datepicker1.value.strftime("%d/%m/%Y")
				data1.cursor_position = len(data1.value)
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
			text="Compensação",
			icon=ft.Icons.CALENDAR_MONTH,
			color=ft.Colors.BLACK,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
			),
			width=matricula.width,
			height=matricula.height,
			on_click=open_date_picker1
		)
		
		# DatePicker para Data a Compensar
		datepicker2 = ft.DatePicker(
			first_date=datetime.datetime(2020, 1, 1),
			last_date=datetime.datetime(2030, 12, 31),
		)
		def on_date2_change(e):
			if datepicker2.value:
				# Primeiro validar se os campos obrigatórios estão preenchidos
				if not validar_campos_obrigatorios(e.control.page):
					# Se não passou na validação, não permite selecionar a data
					data2.value = ""
					data2.update()
					return
				
				data2.value = datepicker2.value.strftime("%d/%m/%Y")
				data2.cursor_position = len(data2.value)
				# Validar datas após mudança da data2
				if validar_datas(e.control.page):
					# Se a validação de datas passou, validar a equipe
					validar_equipe_data(e.control.page, data2.value)
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
			text="A compensar",
			icon=ft.Icons.CALENDAR_MONTH,
			color=ft.Colors.BLACK,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
			),
			width=matricula.width,
			height=matricula.height,
			on_click=open_date_picker2
		)

		form_grid = ft.Column([
			ft.Row([
				matricula, policial
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
			ft.Row([
				nome, equipe
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
			ft.Row([
				btn_data1, data1
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
			ft.Row([
				btn_data2, data2
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
		], spacing=24, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

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

		# Função para gravar compensação
		def gravar_compensacao(e):
			# Validar se todos os campos obrigatórios estão preenchidos
			if not matricula.value.strip():
				mostrar_resultado_gravacao(e.control.page, False, "Matrícula é obrigatória!")
				return
			
			if not data1.value.strip():
				mostrar_resultado_gravacao(e.control.page, False, "Data de Compensação é obrigatória!")
				return
			
			if not data2.value.strip():
				mostrar_resultado_gravacao(e.control.page, False, "Data A Compensar é obrigatória!")
				return
			
			try:
				# Buscar o ID do policial pela matrícula
				query_policial = "SELECT id FROM policiais WHERE matricula = ?"
				result_policial = self.app.db.execute_query(query_policial, (matricula.value.strip(),))
				
				if not result_policial:
					mostrar_resultado_gravacao(e.control.page, False, "Policial não encontrado!")
					return
				
				policial_id = result_policial[0]["id"] if hasattr(result_policial[0], "keys") else result_policial[0][0]
				
				# Converter datas para formato SQL (aaaa-mm-dd)
				from datetime import datetime
				data_compensacao = datetime.strptime(data1.value, "%d/%m/%Y").strftime("%Y-%m-%d")
				data_a_compensar = datetime.strptime(data2.value, "%d/%m/%Y").strftime("%Y-%m-%d")
				
				# Inserir na tabela compensacoes
				query_insert = """
					INSERT INTO compensacoes (policial_id, compensacao, a_compensar)
					VALUES (?, ?, ?)
				"""
				
				success = self.app.db.execute_command(
					query_insert, 
					(policial_id, data_compensacao, data_a_compensar)
				)
				
				if success:
					mostrar_resultado_gravacao(
						e.control.page, 
						True, 
						f"Compensação gravada com sucesso!\n\n"
						f"Policial: {nome.value}\n"
						f"Compensação: {data1.value}\n"
						f"A Compensar: {data2.value}"
					)
					# Limpar o formulário após sucesso
					limpar_formulario(e)
				else:
					mostrar_resultado_gravacao(e.control.page, False, "Erro ao gravar a compensação!")
					
			except ValueError as ve:
				mostrar_resultado_gravacao(e.control.page, False, f"Formato de data inválido: {str(ve)}")
			except Exception as ex:
				mostrar_resultado_gravacao(e.control.page, False, f"Erro inesperado: {str(ex)}")

		# Função para limpar o formulário
		def limpar_formulario(e):
			# Limpar todos os campos
			matricula.value = ""
			policial.value = ""
			nome.value = ""
			equipe.value = ""
			data1.value = ""
			data2.value = ""
			
			# Atualizar os campos na interface
			matricula.update()
			policial.update()
			nome.update()
			equipe.update()
			data1.update()
			data2.update()

		# Botões
		btn_gravar = ft.ElevatedButton(
			text="Gravar",
			style=ft.ButtonStyle(
				color=ft.Colors.BLACK,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.GREEN)),
			icon=ft.Icons.SAVE,
			color=ft.Colors.GREEN,
			width=150,
			bgcolor=ft.Colors.WHITE,
			on_click=gravar_compensacao
		)
		btn_limpar = ft.ElevatedButton(
			text="Limpar",
			width=btn_gravar.width,
			style=ft.ButtonStyle(
				color=ft.Colors.BLACK,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.RED)),
			icon=ft.Icons.DELETE,
			bgcolor=ft.Colors.WHITE,
			color=ft.Colors.RED,
			on_click=limpar_formulario
		)
		btn_row = ft.Row([
			btn_gravar,
			btn_limpar
		], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

		return ft.Column([
			ft.Text("Cadastrar Compensação", size=28, weight=ft.FontWeight.BOLD,
					color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
			ft.Container(height=20),
			form_grid,
			ft.Container(height=30),
			btn_row
		], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
