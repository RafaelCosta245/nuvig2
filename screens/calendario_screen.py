import flet as ft
import uuid
import random
import json
import os
from datetime import datetime, timedelta

from .base_screen import BaseScreen
from database.database_manager import DatabaseManager

# Imports para PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class CalendarioScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "calendario"

	def get_content(self) -> ft.Control:
		# Título da página
		header = ft.Container(
			content=ft.Text(
				"Calendário e escalas",
				size=20,
				weight=ft.FontWeight.BOLD,
				color=ft.Colors.BLACK,
				text_align=ft.TextAlign.CENTER
			),
			padding=ft.padding.only(bottom=10),
			alignment=ft.alignment.center
		)

		pt_weekdays = [
			"Segunda", "Terça", "Quarta",
			"Quinta", "Sexta", "Sábado", "Domingo"
		]

		def exportar_pdf(e):
			try:
				print("[PDF] Iniciando exportação de PDF...")

				# Verificar se temos data válida
				if not data.value or len(data.value) != 10:
					print("[PDF] Erro: Data inválida")
					show_alert_dialog(
						"Erro na Exportação",
						"Data inválida. Por favor, selecione uma data válida no formato dd/mm/aaaa.",
						False,
						e
					)
					return

				data_iso = ddmmyyyy_to_yyyymmdd(data.value)
				if not data_iso:
					print("[PDF] Erro: Não foi possível converter data")
					show_alert_dialog(
						"Erro na Exportação",
						"Erro ao converter data. Verifique o formato da data.",
						False,
						e
					)
					return

				print(f"[PDF] Verificando se existe escala para {data_iso}")

				# Verificar se existe escala para esta data
				existing = db.execute_query("SELECT escala FROM calendario WHERE data = ?", (data_iso,))

				if not existing or len(existing) == 0:
					show_alert_dialog(
						"Nenhuma Escala Encontrada",
						f"Não há escala salva para o dia {data.value}.\n\nPor favor, organize a escala e clique em 'Salvar' antes de exportar o PDF.",
						False,
						e
					)
					return

				# Verificar se a escala não está vazia
				try:
					row = existing[0]
					escala_json = row['escala'] if 'escala' in row.keys() else row[0]
				except:
					row = existing[0]
					escala_json = row[0]

				if not escala_json:
					show_alert_dialog(
						"Escala Vazia",
						f"A escala para o dia {data.value} está vazia.\n\nPor favor, organize a escala e clique em 'Salvar' antes de exportar o PDF.",
						False,
						e
					)
					return

				print(f"[PDF] Escala encontrada, gerando PDF...")

				# Fazer parse do JSON
				try:
					dados_escala = json.loads(escala_json)
				except json.JSONDecodeError as je:
					print(f"[PDF] Erro ao fazer parse do JSON: {je}")
					show_alert_dialog(
						"Erro no JSON",
						"Erro ao processar os dados da escala. O arquivo pode estar corrompido.",
						False,
						e
					)
					return

				# Determinar diretório de saída a partir do banco (roots.save_path) ou app.output_dir
				output_dir = None
				try:
					# Prioriza sempre o caminho salvo na tabela roots (save_path)
					app_ref = getattr(self, 'app', None)
					db_mgr = app_ref.db if (app_ref and hasattr(app_ref, 'db')) else DatabaseManager()
					output_dir = db_mgr.get_root_path("save_path")
					# Fallback: app.output_dir (se existir e for válido)
					if not output_dir or not os.path.isdir(output_dir):
						output_dir = getattr(app_ref, 'output_dir', None) if app_ref else None
					# Fallback final: diretório atual
					if not output_dir or not os.path.isdir(output_dir):
						output_dir = os.getcwd()
				except Exception as config_ex:
					print(f"[PDF] Falha ao obter diretório de saída (roots.save_path): {config_ex}")
					output_dir = os.getcwd()

				# Gerar nome do arquivo
				data_formatada = data.value.replace("/", "-")
				nome_arquivo = f"Escala_{data_formatada}.pdf"
				caminho_pdf = os.path.join(output_dir, nome_arquivo)

				# Garantir que o diretório exista
				try:
					os.makedirs(output_dir, exist_ok=True)
				except Exception as mk_ex:
					print(f"[PDF] Aviso: não foi possível criar diretório de saída '{output_dir}': {mk_ex}")

				print(f"[PDF] Gerando PDF: {caminho_pdf}")

				# Gerar o PDF
				_gerar_pdf_escala(dados_escala, data.value, caminho_pdf, equipe)

				print(f"[PDF] ✓ PDF gerado com sucesso: {caminho_pdf}")
				show_alert_dialog(
					"PDF Gerado com Sucesso",
					f"O PDF da escala foi gerado com sucesso!\n\nArquivo salvo em:\n{caminho_pdf}",
					True,
					e
				)

			except Exception as ex:
				print(f"[PDF] Erro ao exportar PDF: {ex}")
				import traceback
				traceback.print_exc()
				show_alert_dialog(
					"Erro na Exportação",
					f"Ocorreu um erro inesperado ao gerar o PDF:\n\n{str(ex)}\n\nVerifique o console para mais detalhes.",
					False,
					e
				)

		def _gerar_pdf_escala(dados_escala, data_ddmmyyyy, caminho_pdf, equipe_letra):
			"""Gera o PDF da escala baseado no template da imagem"""
			try:
				print(f"[DEBUG PDF] Iniciando geração de PDF")
				print(f"[DEBUG PDF] Dados da escala recebidos:")
				import json
				print(json.dumps(dados_escala, ensure_ascii=False, indent=2))
				# Criar documento PDF
				doc = SimpleDocTemplate(
					caminho_pdf,
					pagesize=A4,
					rightMargin=1 * cm,
					leftMargin=1 * cm,
					topMargin=1 * cm,
					bottomMargin=1 * cm
				)

				# Lista para armazenar elementos do PDF
				elements = []

				# Estilos
				styles = getSampleStyleSheet()
				title_style = ParagraphStyle(
					'CustomTitle',
					parent=styles['Heading1'],
					fontSize=14,
					spaceAfter=12,
					alignment=TA_CENTER,
					fontName='Helvetica-Bold'
				)

				subtitle_style = ParagraphStyle(
					'CustomSubtitle',
					parent=styles['Normal'],
					fontSize=12,
					spaceAfter=6,
					alignment=TA_CENTER,
					fontName='Helvetica-Bold'
				)

				# Adicionar logo se existir
				logo_path = "assets/icons/ceara.png"
				if os.path.exists(logo_path):
					try:
						logo = Image(logo_path, width=3 * cm, height=3 * cm)
						logo.hAlign = 'CENTER'
						elements.append(logo)
						elements.append(Spacer(1, 0.5 * cm))
					except Exception as logo_ex:
						print(f"[PDF] Erro ao carregar logo: {logo_ex}")

				# Cabeçalho
				elements.append(Paragraph("GOVERNO DO ESTADO DO CEARÁ", title_style))
				elements.append(
					Paragraph("SECRETARIA DA ADMINISTRAÇÃO PENITENCIÁRIA E RESSOCIALIZAÇÃO", subtitle_style))
				elements.append(Spacer(1, 0.5 * cm))

				# Título da escala
				elements.append(Paragraph(f"EQUIPE DELTA", title_style))
				# Usar o dia da semana já calculado
				if dia_semana_atual:
					elements.append(Paragraph(f"{dia_semana_atual} - {data_ddmmyyyy}", subtitle_style))
				else:
					elements.append(Paragraph(f"- {data_ddmmyyyy}", subtitle_style))
				elements.append(Spacer(1, 0.8 * cm))

				# Tabela principal - Plantão e Extras
				tabela_principal_data = []

				# Cabeçalho da tabela principal
				tabela_principal_data.append([
					"", "PLANTÃO", "EXTRAS DIURNA", "EXTRAS NOTURNA"
				])

				# Dados dos acessos
				acessos = ["ACESSO 1", "ACESSO 2", "ACESSO 3"]
				colunas_acesso = ["Acesso 01", "Acesso 02", "Acesso 03"]

				for i, (acesso_nome, coluna_nome) in enumerate(zip(acessos, colunas_acesso)):
					plantao_list = []
					extras_diurna_list = []
					extras_noturna_list = []

					# Buscar policiais do plantão (acesso)
					if coluna_nome in dados_escala:
						print(f"[DEBUG PDF] Processando coluna {coluna_nome}")
						for pol in dados_escala[coluna_nome]:
							nome = pol.get("nome", "")
							status = pol.get("status", "")
							permuta_info = pol.get("permuta_info")
							compensacao_info = pol.get("compensacao_info")
							tac_info = pol.get("tac_info")
							
							print(f"[DEBUG PDF] Policial: {nome}, Status: {status}, Permuta Info: {permuta_info}, Compensação Info: {compensacao_info}, TAC Info: {tac_info}")
							
							if status == "Plantão":
								plantao_list.append(nome)
							elif status == "Compensação":
								# Verificar se há informações de compensação
								print(f"[DEBUG PDF] Processando compensação para {nome}")
								if compensacao_info and compensacao_info.get("tipo") == "trabalha":
									nome_com_anotacao = f"{nome} (CP. {compensacao_info.get('data_compensada', 'N/A')})"
									print(f"[DEBUG PDF] Nome com anotação COMPENSAÇÃO: {nome_com_anotacao}")
								else:
									nome_com_anotacao = nome
									print(f"[DEBUG PDF] Nome sem anotação: {nome_com_anotacao}")
								plantao_list.append(nome_com_anotacao)  # Policiais de compensação também vão para plantão
							elif status == "TAC":
								# Verificar se há informações de TAC
								print(f"[DEBUG PDF] Processando TAC para {nome}")
								if tac_info:
									nome_com_anotacao = f"{nome} (TAC)"
									print(f"[DEBUG PDF] Nome com anotação TAC: {nome_com_anotacao}")
								else:
									nome_com_anotacao = nome
									print(f"[DEBUG PDF] Nome sem anotação: {nome_com_anotacao}")
								plantao_list.append(nome_com_anotacao)  # Policiais de TAC também vão para plantão
							elif status == "Permuta":
								# Verificar se há informações de permuta
								print(f"[DEBUG PDF] Processando permuta para {nome}")
								if permuta_info and permuta_info.get("tipo") == "entra":
									nome_com_anotacao = f"{nome} (P.O. {permuta_info.get('com', 'N/A')})"
									print(f"[DEBUG PDF] Nome com anotação ENTRA: {nome_com_anotacao}")
								else:
									nome_com_anotacao = nome
									print(f"[DEBUG PDF] Nome sem anotação: {nome_com_anotacao}")
								plantao_list.append(nome_com_anotacao)  # Policiais de permuta também vão para plantão
							elif status == "Extra diurno":
								extras_diurna_list.append(nome)
							elif status == "Extra noturno":
								extras_noturna_list.append(nome)

					# Formatar listas
					plantao_text = "\n".join([f"{j + 1}. {nome}" for j, nome in enumerate(plantao_list)])
					extras_diurna_text = "\n".join([f"{j + 1}. {nome}" for j, nome in enumerate(extras_diurna_list)])
					extras_noturna_text = "\n".join([f"{j + 1}. {nome}" for j, nome in enumerate(extras_noturna_list)])

					tabela_principal_data.append([
						acesso_nome,
						plantao_text,
						extras_diurna_text,
						extras_noturna_text
					])

				# Adicionar linha OBLL
				obll_list = []
				if "OBLL" in dados_escala:
					for pol in dados_escala["OBLL"]:
						nome = pol.get("nome", "")
						obll_list.append(nome)

				obll_text = "\n".join([f"{j + 1}. {nome}" for j, nome in enumerate(obll_list)])
				tabela_principal_data.append([
					"OBLL",
					obll_text,
					"",
					""
				])

				# Criar tabela principal - Aumentando largura da coluna PLANTÃO e diminuindo as outras
				tabela_principal = Table(tabela_principal_data, colWidths=[2.5 * cm, 6.5 * cm, 3.5 * cm, 3.5 * cm])
				tabela_principal.setStyle(TableStyle([
					('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
					('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
					('ALIGN', (0, 0), (-1, -1), 'CENTER'),
					('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
					('FONTSIZE', (0, 0), (-1, 0), 10),
					('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
					('FONTSIZE', (0, 1), (-1, -1), 9),
					('BOTTOMPADDING', (0, 0), (-1, 0), 12),
					('GRID', (0, 0), (-1, -1), 1, colors.black),
					('VALIGN', (0, 0), (-1, -1), 'TOP'),
				]))

				elements.append(tabela_principal)
				elements.append(Spacer(1, 0.5 * cm))

				# Tabela secundária - Férias, Licenças, Ausentes
				tabela_secundaria_data = []

				# Cabeçalho da tabela secundária
				tabela_secundaria_data.append([
					"FÉRIAS", "LICENÇAS", "AUSENTES"
				])

				# Dados
				ferias_list = []
				licencas_list = []
				ausentes_list = []

				if "Férias" in dados_escala:
					for pol in dados_escala["Férias"]:
						nome = pol.get("nome", "")
						ferias_list.append(nome)

				if "Licenças" in dados_escala:
					for pol in dados_escala["Licenças"]:
						nome = pol.get("nome", "")
						licencas_list.append(nome)

				if "Ausências" in dados_escala:
					print(f"[DEBUG PDF] Processando Ausências")
					for pol in dados_escala["Ausências"]:
						nome = pol.get("nome", "")
						status = pol.get("status", "")
						permuta_info = pol.get("permuta_info")
						compensacao_info = pol.get("compensacao_info")
						
						print(f"[DEBUG PDF] Ausente: {nome}, Status: {status}, Permuta Info: {permuta_info}, Compensação Info: {compensacao_info}")
						
						# Verificar se é ausente por permuta
						if status == "Permuta":
							print(f"[DEBUG PDF] Processando ausente por permuta: {nome}")
							if permuta_info and permuta_info.get("tipo") == "sai":
								nome_com_anotacao = f"{nome} (PERM.)"
								print(f"[DEBUG PDF] Nome com anotação SAI: {nome_com_anotacao}")
							else:
								nome_com_anotacao = nome
								print(f"[DEBUG PDF] Nome sem anotação: {nome_com_anotacao}")
							ausentes_list.append(nome_com_anotacao)
						# Verificar se é ausente por compensação
						elif status == "Compensação":
							print(f"[DEBUG PDF] Processando ausente por compensação: {nome}")
							if compensacao_info and compensacao_info.get("tipo") == "ausente":
								nome_com_anotacao = f"{nome} (CP. {compensacao_info.get('data_trabalhada', 'N/A')})"
								print(f"[DEBUG PDF] Nome com anotação COMPENSAÇÃO: {nome_com_anotacao}")
							else:
								nome_com_anotacao = nome
								print(f"[DEBUG PDF] Nome sem anotação: {nome_com_anotacao}")
							ausentes_list.append(nome_com_anotacao)
						else:
							ausentes_list.append(nome)

				# Formatar listas
				ferias_text = "\n".join([f"{j + 1}. {nome}" for j, nome in enumerate(ferias_list)])
				licencas_text = "\n".join([f"{j + 1}. {nome}" for j, nome in enumerate(licencas_list)])
				ausentes_text = "\n".join([f"{j + 1}. {nome}" for j, nome in enumerate(ausentes_list)])

				tabela_secundaria_data.append([
					ferias_text,
					licencas_text,
					ausentes_text
				])

				# Criar tabela secundária
				tabela_secundaria = Table(tabela_secundaria_data, colWidths=[5.3 * cm, 5.3 * cm, 5.3 * cm],
										  rowHeights=[0.8 * cm, 3 * cm])
				tabela_secundaria.setStyle(TableStyle([
					('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
					('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
					('ALIGN', (0, 0), (-1, -1), 'CENTER'),
					('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
					('FONTSIZE', (0, 0), (-1, 0), 10),
					('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
					('FONTSIZE', (0, 1), (-1, -1), 9),
					('BOTTOMPADDING', (0, 0), (-1, 0), 12),
					('TOPPADDING', (0, 1), (-1, -1), 8),
					('BOTTOMPADDING', (0, 1), (-1, -1), 8),
					('GRID', (0, 0), (-1, -1), 1, colors.black),
					('VALIGN', (0, 0), (-1, -1), 'TOP'),
				]))

				elements.append(tabela_secundaria)
				elements.append(Spacer(1, 0.8 * cm))

				# Observações (similar ao template)
				obs_data = [
					["OBS 01", "OBS 02", "OBS 03"],
					[
						""
					]
				]

				tabela_obs = Table(obs_data, colWidths=[5.3 * cm, 5.3 * cm, 5.3 * cm], rowHeights=[0.8 * cm, 2.5 * cm])
				tabela_obs.setStyle(TableStyle([
					('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
					('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
					('ALIGN', (0, 0), (-1, -1), 'CENTER'),
					('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
					('FONTSIZE', (0, 0), (-1, 0), 10),
					('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
					('FONTSIZE', (0, 1), (-1, -1), 8),
					('BOTTOMPADDING', (0, 0), (-1, 0), 12),
					('TOPPADDING', (0, 1), (-1, -1), 8),
					('BOTTOMPADDING', (0, 1), (-1, -1), 8),
					('LEFTPADDING', (0, 1), (-1, -1), 6),
					('RIGHTPADDING', (0, 1), (-1, -1), 6),
					('GRID', (0, 0), (-1, -1), 1, colors.black),
					('VALIGN', (0, 0), (-1, -1), 'TOP'),
				]))

				elements.append(tabela_obs)

				# Gerar o PDF
				doc.build(elements)
				print(f"[PDF] ✓ PDF gerado com sucesso: {caminho_pdf}")

			except Exception as ex:
				print(f"[PDF] Erro ao gerar PDF: {ex}")
				raise ex

		def deletar_escala(e):
			try:
				print("[Deletar] Iniciando exclusão de escala...")

				# Verificar se temos data válida
				if not data.value or len(data.value) != 10:
					print("[Deletar] Erro: Data inválida")
					show_alert_dialog(
						"Erro na Exclusão",
						"Data inválida. Por favor, selecione uma data válida no formato dd/mm/aaaa.",
						False,
						e
					)
					return

				data_iso = ddmmyyyy_to_yyyymmdd(data.value)
				if not data_iso:
					print("[Deletar] Erro: Não foi possível converter data")
					show_alert_dialog(
						"Erro na Exclusão",
						"Não foi possível converter a data. Verifique o formato (dd/mm/aaaa).",
						False,
						e
					)
					return

				print(f"[Deletar] Verificando se existe escala para {data_iso}")

				# Verificar se existe escala para esta data
				existing = db.execute_query("SELECT escala FROM calendario WHERE data = ?", (data_iso,))

				if not existing or len(existing) == 0:
					show_alert_dialog(
						"Nenhuma Escala Encontrada",
						f"Não foi encontrada nenhuma escala salva para o dia {data.value}.\n\nNão há nada para excluir.",
						False,
						e
					)
					return

				# Verificar se a escala não está vazia
				try:
					row = existing[0]
					escala_atual = row['escala'] if 'escala' in row.keys() else row[0]
				except:
					row = existing[0]
					escala_atual = row[0]

				if not escala_atual:
					show_alert_dialog(
						"Escala Vazia",
						f"A escala para o dia {data.value} já está vazia.\n\nNão há nada para excluir.",
						False,
						e
					)
					return

				print(f"[Deletar] Escala encontrada, mostrando confirmação...")

				# Mostrar dialog de confirmação
				show_confirmation_dialog(data.value, data_iso, e)

			except Exception as ex:
				print(f"[Deletar] Erro ao verificar escala: {ex}")
				import traceback
				traceback.print_exc()
				show_alert_dialog(
					"Erro na Exclusão",
					f"Ocorreu um erro inesperado ao verificar a escala:\n\n{str(ex)}",
					False,
					e
				)

		def show_confirmation_dialog(data_ddmmyyyy: str, data_iso: str, event):
			"""Mostra dialog de confirmação para exclusão"""
			try:
				# Obter page do evento
				page = None
				if event:
					if hasattr(event, 'page') and event.page:
						page = event.page
					elif hasattr(event, 'control') and hasattr(event.control, 'page') and event.control.page:
						page = event.control.page

				if not page:
					print(f"[Confirmação] Erro: Não foi possível obter page")
					return

				import flet as ft

				def confirmar_exclusao(e):
					page.close(dialog_confirmacao)
					executar_exclusao(data_ddmmyyyy, data_iso, event)

				def cancelar_exclusao(e):
					page.close(dialog_confirmacao)
					print(f"[Confirmação] Exclusão cancelada pelo usuário")

				# Criar dialog de confirmação
				dialog_confirmacao = ft.AlertDialog(
					modal=True,
					title=ft.Row(
						controls=[
							ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE, size=24),
							ft.Text("Confirmar Exclusão", color=ft.Colors.ORANGE, weight=ft.FontWeight.BOLD, size=16)
						],
						alignment=ft.MainAxisAlignment.START,
						spacing=10
					),
					content=ft.Text(
						f"Tem certeza que deseja excluir a escala do dia {data_ddmmyyyy}?\n\nEsta ação não pode ser desfeita.",
						size=14
					),
					actions=[
						ft.TextButton(
							text="Cancelar",
							on_click=cancelar_exclusao
						),
						ft.TextButton(
							text="Sim, Excluir",
							on_click=confirmar_exclusao,
							style=ft.ButtonStyle(color=ft.Colors.RED)
						)
					],
					actions_alignment=ft.MainAxisAlignment.END,
				)

				page.open(dialog_confirmacao)
				print(f"[Confirmação] Dialog de confirmação aberto")

			except Exception as ex:
				print(f"[Confirmação] Erro ao mostrar confirmação: {ex}")
				import traceback
				traceback.print_exc()

		def executar_exclusao(data_ddmmyyyy: str, data_iso: str, event):
			"""Executa a exclusão da escala após confirmação"""
			try:
				print(f"[Executar] Excluindo escala para {data_iso}")

				# Executar UPDATE para limpar a coluna escala
				if hasattr(db, 'execute_non_query'):
					result = db.execute_non_query(
						"UPDATE calendario SET escala = NULL WHERE data = ?",
						(data_iso,)
					)
				else:
					result = db.execute_query(
						"UPDATE calendario SET escala = NULL WHERE data = ?",
						(data_iso,)
					)

				print(f"[Executar] UPDATE executado - Resultado: {result}")

				# Forçar commit
				if hasattr(db, 'commit'):
					db.commit()
					print(f"[Executar] Commit executado")
				elif hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
					db.connection.commit()
					print(f"[Executar] Commit da conexão executado")

				# Verificar se foi excluído
				verificacao = db.execute_query("SELECT escala FROM calendario WHERE data = ?", (data_iso,))
				if verificacao and len(verificacao) > 0:
					try:
						row = verificacao[0]
						escala_verificacao = row['escala'] if 'escala' in row.keys() else row[0]
					except:
						row = verificacao[0]
						escala_verificacao = row[0]

					if not escala_verificacao:
						print(f"[Executar] ✓ Escala excluída com sucesso")
						show_alert_dialog(
							"Exclusão Concluída",
							f"A escala do dia {data_ddmmyyyy} foi excluída com sucesso!\n\nClique em Ok para fechar",
							True,
							event
						)
						# Recarregar a tela para mostrar nova distribuição
						refresh_tabela_para_data_atual()
					else:
						print(f"[Executar] ✗ Escala não foi excluída")
						show_alert_dialog(
							"Erro na Exclusão",
							f"Houve um problema ao excluir a escala do dia {data_ddmmyyyy}.\n\nA escala ainda está presente no banco.",
							False,
							event
						)
				else:
					print(f"[Executar] ✗ Registro não encontrado após exclusão")
					show_alert_dialog(
						"Erro na Exclusão",
						f"Não foi possível verificar a exclusão da escala do dia {data_ddmmyyyy}.",
						False,
						event
					)

			except Exception as ex:
				print(f"[Executar] Erro ao excluir escala: {ex}")
				import traceback
				traceback.print_exc()
				show_alert_dialog(
					"Erro na Exclusão",
					f"Ocorreu um erro inesperado ao excluir a escala:\n\n{str(ex)}",
					False,
					event
				)

		def show_alert_dialog(title: str, message: str, is_success: bool = True, event=None):
			"""Mostra um dialog de alerta com título e mensagem"""
			try:
				# Tentar diferentes formas de obter a page
				page = None

				# Método 0: Tentar através do evento passado
				if event:
					try:
						if hasattr(event, 'page') and event.page:
							page = event.page
							print(f"[Alert] Page obtida via event.page")
						elif hasattr(event, 'control') and hasattr(event.control, 'page') and event.control.page:
							page = event.control.page
							print(f"[Alert] Page obtida via event.control.page")
					except:
						pass

				# Método 1: self.page
				if not page and hasattr(self, 'page') and self.page:
					page = self.page
					print(f"[Alert] Page obtida via self.page")

				# Método 2: Tentar através de controles existentes
				if not page:
					try:
						if hasattr(data, 'page') and data.page:
							page = data.page
							print(f"[Alert] Page obtida via data.page")
					except:
						pass

				# Método 3: Tentar através do botão salvar
				if not page:
					try:
						# Vamos tentar obter através de qualquer controle que tenha page
						for attr_name in dir(self):
							attr = getattr(self, attr_name, None)
							if hasattr(attr, 'page') and attr.page:
								page = attr.page
								print(f"[Alert] Page obtida via {attr_name}.page")
								break
					except:
						pass

				# Debug: mostrar informações sobre self
				print(f"[Alert] Debug - self type: {type(self)}")
				print(f"[Alert] Debug - self.page exists: {hasattr(self, 'page')}")
				print(f"[Alert] Debug - self.page value: {getattr(self, 'page', 'NOT_FOUND')}")

				if not page:
					print(f"[Alert] ERRO: Não foi possível obter page de nenhuma forma")
					print(f"[Alert] {title}: {message}")
					return

				# Importar flet no escopo da função
				import flet as ft

				# Definir cor e ícone baseado no tipo
				if is_success:
					icon = ft.Icons.CHECK_CIRCLE
					icon_color = ft.Colors.GREEN
					title_color = ft.Colors.GREEN
				else:
					icon = ft.Icons.ERROR
					icon_color = ft.Colors.RED
					title_color = ft.Colors.RED

				# Criar o dialog seguindo o padrão do exemplo
				dialog = ft.AlertDialog(
					modal=True,
					title=ft.Row(
						controls=[
							ft.Icon(icon, color=icon_color, size=24),
							ft.Text(title, color=title_color, weight=ft.FontWeight.BOLD, size=16)
						],
						alignment=ft.MainAxisAlignment.START,
						spacing=10
					),
					content=ft.Text(message, size=14),
					actions=[
						ft.TextButton(
							text="OK",
							on_click=lambda e: page.close(dialog)
						)
					],
					actions_alignment=ft.MainAxisAlignment.END,
					on_dismiss=lambda e: print(f"[Alert] Dialog fechado: {title}")
				)

				# Mostrar o dialog conforme o exemplo (sem adicionar ao overlay)
				page.open(dialog)
				print(f"[Alert] Dialog aberto: {title}")

			except Exception as ex:
				print(f"[Alert] Erro ao mostrar dialog: {ex}")
				import traceback
				traceback.print_exc()

		def _buscar_info_permuta(policial_id: str, data_iso: str):
			"""Busca informações de permuta para um policial em uma data específica"""
			try:
				print(f"[DEBUG PERMUTA] Buscando permuta para policial_id: {policial_id}, data: {data_iso}")
				
				if not policial_id or not data_iso:
					print(f"[DEBUG PERMUTA] Parâmetros inválidos: policial_id={policial_id}, data_iso={data_iso}")
					return None
				
				# Buscar permutas onde este policial é solicitante (sai na data)
				rows_solicitante = db.execute_query(
					"SELECT permutado FROM permutas WHERE solicitante = ? AND data_solicitante = ?",
					(policial_id, data_iso)
				)
				print(f"[DEBUG PERMUTA] Rows solicitante: {rows_solicitante}")
				
				if rows_solicitante and len(rows_solicitante) > 0:
					permutado_id = rows_solicitante[0]["permutado"] if "permutado" in rows_solicitante[0].keys() else rows_solicitante[0][0]
					print(f"[DEBUG PERMUTA] Permutado ID: {permutado_id}")
					# Buscar nome do permutado
					perm_rows = db.execute_query("SELECT nome, qra FROM policiais WHERE id = ?", (permutado_id,))
					if perm_rows and len(perm_rows) > 0:
						permutado_nome = perm_rows[0]["qra"] if "qra" in perm_rows[0].keys() else perm_rows[0]["nome"]
						resultado = {"tipo": "sai", "com": permutado_nome}
						print(f"[DEBUG PERMUTA] Resultado SAI: {resultado}")
						return resultado
				
				# Buscar permutas onde este policial é permutado (entra na data)
				rows_permutado = db.execute_query(
					"SELECT solicitante FROM permutas WHERE permutado = ? AND data_permutado = ?",
					(policial_id, data_iso)
				)
				print(f"[DEBUG PERMUTA] Rows permutado: {rows_permutado}")
				
				if rows_permutado and len(rows_permutado) > 0:
					solicitante_id = rows_permutado[0]["solicitante"] if "solicitante" in rows_permutado[0].keys() else rows_permutado[0][0]
					print(f"[DEBUG PERMUTA] Solicitante ID: {solicitante_id}")
					# Buscar nome do solicitante
					sol_rows = db.execute_query("SELECT nome, qra FROM policiais WHERE id = ?", (solicitante_id,))
					if sol_rows and len(sol_rows) > 0:
						solicitante_nome = sol_rows[0]["qra"] if "qra" in sol_rows[0].keys() else sol_rows[0]["nome"]
						resultado = {"tipo": "entra", "com": solicitante_nome}
						print(f"[DEBUG PERMUTA] Resultado ENTRA: {resultado}")
						return resultado
				
				print(f"[DEBUG PERMUTA] Nenhuma permuta encontrada para {policial_id}")
				return None
			except Exception as ex:
				print(f"[Permuta Info] Erro ao buscar info de permuta: {ex}")
				return None

		def salvar_escala(e):
			try:
				print("Salvando escala...")

				# Verificar se temos data válida
				if not data.value or len(data.value) != 10:
					print("[Salvar] Erro: Data inválida")
					show_alert_dialog(
						"Erro no Salvamento",
						"Data inválida. Por favor, selecione uma data válida no formato dd/mm/aaaa.",
						False,
						e
					)
					return

				data_iso = ddmmyyyy_to_yyyymmdd(data.value)
				if not data_iso:
					print("[Salvar] Erro: Não foi possível converter data")
					show_alert_dialog(
						"Erro no Salvamento",
						"Não foi possível converter a data. Verifique o formato (dd/mm/aaaa).",
						False,
						e
					)
					return

				print(f"[Salvar] Salvando escala para data: {data_iso}")

				# Mapear tipos para status conforme o JSON de exemplo
				tipo_para_status = {
					"padrao": "Plantão",
					"obll": "OBLL",
					"ferias": "Férias",
					"licencas": "Licença",
					"ausencias": "Ausência",
					"compensacao": "Compensação",
					"permuta": "Permuta",
					"extra_diurno": "Extra diurno",
					"extra_noturno": "Extra noturno",
					"tac": "TAC"
				}

				# Construir estrutura JSON
				dados = {}

				# Mapear colunas para nomes no JSON
				col_mapping = {
					"col1": "Acesso 01",
					"col2": "Acesso 02",
					"col3": "Acesso 03",
					"col4": "OBLL",
					"col5": "Férias",
					"col6": "Licenças",
					"col7": "Ausências"
				}

				# Processar cada coluna
				for col_key, col_name in col_mapping.items():
					dados[col_name] = []

					for item in col_items[col_key]:
						item_data = getattr(item, "data", "")
						policial_info = id_map.get(item_data, {})

						nome = policial_info.get("qra") or policial_info.get("nome") or "DESCONHECIDO"
						tipo = policial_info.get("tipo", "padrao")
						status = tipo_para_status.get(tipo, "Plantão")

						print(f"[DEBUG SALVAR] Processando {nome}: item_data={item_data}, tipo={tipo}, status={status}")

						# Verificar se é permuta e buscar informações adicionais do id_map
						permuta_info = None
						if tipo == "permuta":
							print(f"[DEBUG SALVAR] Policial {nome} é permuta, buscando info no id_map...")
							permuta_info = policial_info.get("permuta_info")
							print(f"[DEBUG SALVAR] Permuta info para {nome}: {permuta_info}")
						
						# Verificar se é compensação e buscar informações adicionais do id_map
						compensacao_info = None
						if tipo == "compensacao":
							print(f"[DEBUG SALVAR] Policial {nome} é compensação, buscando info no id_map...")
							compensacao_info = policial_info.get("compensacao_info")
							print(f"[DEBUG SALVAR] Compensação info para {nome}: {compensacao_info}")
						
						# Verificar se é TAC e buscar informações adicionais do id_map
						tac_info = None
						if tipo == "tac":
							print(f"[DEBUG SALVAR] Policial {nome} é TAC, buscando info no id_map...")
							tac_info = policial_info.get("tac_info")
							print(f"[DEBUG SALVAR] TAC info para {nome}: {tac_info}")
						
						policial_data = {
							"nome": nome,
							"status": status,
							"permuta_info": permuta_info,
							"compensacao_info": compensacao_info,
							"tac_info": tac_info
						}
						print(f"[DEBUG SALVAR] Adicionando à coluna {col_name}: {policial_data}")
						dados[col_name].append(policial_data)

				# Converter para JSON string
				import json
				escala_json = json.dumps(dados, ensure_ascii=False, indent=2)

				print(f"[Salvar] JSON gerado:")
				print(escala_json)

				# Salvar no banco de dados
				print(f"[Salvar] Iniciando salvamento no banco...")

				# Primeiro verificar se já existe registro para esta data
				existing = db.execute_query("SELECT id FROM calendario WHERE data = ?", (data_iso,))
				print(
					f"[Salvar] Verificando se existe registro para {data_iso}: {len(existing) if existing else 0} registros encontrados")

				# Vamos tentar usar execute_non_query se disponível, ou forçar commit
				try:
					if existing and len(existing) > 0:
						# Atualizar registro existente
						print(f"[Salvar] Executando UPDATE...")
						if hasattr(db, 'execute_non_query'):
							result = db.execute_non_query(
								"UPDATE calendario SET escala = ? WHERE data = ?",
								(escala_json, data_iso)
							)
						else:
							result = db.execute_query(
								"UPDATE calendario SET escala = ? WHERE data = ?",
								(escala_json, data_iso)
							)
						print(f"[Salvar] UPDATE executado - Resultado: {result}")
					else:
						# Inserir novo registro
						equipe_atual = equipe if equipe else "A"
						print(f"[Salvar] Executando INSERT com equipe {equipe_atual}...")
						if hasattr(db, 'execute_non_query'):
							result = db.execute_non_query(
								"INSERT INTO calendario (data, equipe, escala) VALUES (?, ?, ?)",
								(data_iso, equipe_atual, escala_json)
							)
						else:
							result = db.execute_query(
								"INSERT INTO calendario (data, equipe, escala) VALUES (?, ?, ?)",
								(data_iso, equipe_atual, escala_json)
							)
						print(f"[Salvar] INSERT executado - Resultado: {result}")

					# Forçar commit se o método existir
					if hasattr(db, 'commit'):
						db.commit()
						print(f"[Salvar] Commit executado")
					elif hasattr(db, 'connection') and hasattr(db.connection, 'commit'):
						db.connection.commit()
						print(f"[Salvar] Commit da conexão executado")

				except Exception as db_ex:
					print(f"[Salvar] Erro na operação de banco: {db_ex}")
					raise db_ex

				# Verificar se realmente foi salvo
				print(f"[Salvar] Verificando se foi salvo...")
				verificacao = db.execute_query("SELECT id, data, equipe, escala FROM calendario WHERE data = ?",
											   (data_iso,))
				if verificacao and len(verificacao) > 0:
					print(f"[Salvar] ✓ Verificação: Escala foi salva corretamente no banco")

					# Acessar dados do sqlite3.Row usando índices ou chaves
					row = verificacao[0]
					try:
						# Tentar acessar por chave primeiro
						row_id = row['id'] if 'id' in row.keys() else row[0]
						row_data = row['data'] if 'data' in row.keys() else row[1]
						row_equipe = row['equipe'] if 'equipe' in row.keys() else row[2]
						row_escala = row['escala'] if 'escala' in row.keys() else row[3]
					except:
						# Fallback para índices
						row_id = row[0]
						row_data = row[1]
						row_equipe = row[2]
						row_escala = row[3]

					print(f"[Salvar] Registro encontrado: ID={row_id}, Data={row_data}, Equipe={row_equipe}")

					if row_escala:
						print(f"[Salvar] ✓ Coluna escala contém dados (tamanho: {len(row_escala)} caracteres)")
						print(f"[Salvar] ✓ SUCESSO: Escala foi salva corretamente!")
					else:
						print(f"[Salvar] ✗ Coluna escala está vazia ou NULL")
				else:
					print(f"[Salvar] ✗ ERRO: Escala não foi encontrada no banco após salvamento!")

				# Se chegou até aqui, verificar se realmente foi salvo
				if row_escala:
					print("[Salvar] Escala salva com sucesso!")
					show_alert_dialog(
						"Salvamento Concluído",
						f"A escala foi salva com sucesso para o dia {data.value}!\n\nClique em Ok para fechar",
						True,
						e
					)
				else:
					print("[Salvar] Erro: Escala não foi salva corretamente")
					show_alert_dialog(
						"Erro no Salvamento",
						f"Houve um problema ao salvar a escala para o dia {data.value}.\n\nA escala não foi encontrada no banco após o salvamento.",
						False,
						e
					)

			except Exception as ex:
				print(f"[Salvar] Erro ao salvar escala: {ex}")
				import traceback
				traceback.print_exc()
				show_alert_dialog(
					"Erro no Salvamento",
					f"Ocorreu um erro inesperado ao salvar a escala:\n\n{str(ex)}\n\nVerifique o console para mais detalhes.",
					False,
					e
				)

		def open_date_picker(e):
			# Resolve page from event/control/self
			page = getattr(e, "page", None)
			if page is None and hasattr(e, "control") and hasattr(e.control, "page"):
				page = e.control.page
			if page is None:
				page = self.page
			if datepicker not in page.overlay:
				page.overlay.append(datepicker)
				page.update()
			page.open(datepicker)

		datepicker = ft.DatePicker(
			first_date=datetime(2020, 1, 1),
			last_date=datetime(2030, 12, 31),
		)

		# Tenta anexar o datepicker ao overlay ao montar a tela
		try:
			if self.page and datepicker not in self.page.overlay:
				self.page.overlay.append(datepicker)
		except Exception:
			pass

		weekday = ""
		equipe = ""
		dia_semana_atual = ""  # Variável para armazenar o dia da semana atual

		def atualizar_dia_semana():
			"""Atualiza o dia da semana baseado no valor atual de data.value"""
			nonlocal dia_semana_atual
			try:
				if data.value and len(data.value) == 10:
					# Converter dd/mm/yyyy para objeto datetime
					dia, mes, ano = data.value.split("/")
					data_obj = datetime(int(ano), int(mes), int(dia))
					dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
					dia_semana_atual = dias_semana[data_obj.weekday()]
					print(f"[Dia Semana] Atualizado para: {dia_semana_atual} ({data.value})")
				else:
					dia_semana_atual = ""
					print(f"[Dia Semana] Data inválida: {data.value}")
			except Exception as ex:
				dia_semana_atual = ""
				print(f"[Dia Semana] Erro ao calcular: {ex}")

		# --- Helpers de data ---
		def ddmmyyyy_to_yyyymmdd(s: str) -> str:
			try:
				parts = s.split("/")
				if len(parts) == 3 and all(parts):
					return f"{parts[2]}-{parts[1]}-{parts[0]}"
				return ""
			except Exception:
				return ""

		def yyyymmdd_to_ddmmyyyy(s: str) -> str:
			try:
				parts = s.split("-")
				if len(parts) == 3 and all(parts):
					return f"{parts[2]}/{parts[1]}/{parts[0]}"
				return ""
			except Exception:
				return ""

		def is_valid_ddmmyyyy(s: str) -> bool:
			if not s or len(s) != 10:
				return False
			try:
				datetime.strptime(s, "%d/%m/%Y")
				return True
			except ValueError:
				return False

		# --- DB Manager ---
		db = DatabaseManager()

		def on_date_change(e):
			# disparado ao selecionar data no DatePicker
			if datepicker.value:
				ddmmyyyy = datepicker.value.strftime("%d/%m/%Y")
				data.value = ddmmyyyy
				data.cursor_position = len(data.value)
				# Buscar equipe e atualizar textos
				query_date = ddmmyyyy_to_yyyymmdd(ddmmyyyy)
				if query_date:
					equipe_result = db.get_equipe_by_data(query_date) or ""
					# atualizar variáveis de contexto
					nonlocal weekday, equipe
					# Definir nome do dia da semana em português
					weekday = pt_weekdays[datepicker.value.weekday()]
					equipe = equipe_result
					team_text.value = f"{weekday} - Equipe {equipe}"
					# Atualiza a tabela dinâmica
					try:
						refresh_tabela_para_data_atual()
					except Exception:
						pass
				e.control.page.update()

		datepicker.on_change = on_date_change

		btn_data = ft.ElevatedButton(
			text="Selecionar",
			icon=ft.Icons.CALENDAR_MONTH,
			color=ft.Colors.BLACK,
			bgcolor=ft.Colors.WHITE,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=4),
				side=ft.BorderSide(
					width=1,
					color=ft.Colors.BLACK
				)
			),
			tooltip="Clique para escolher a data ou digite no campo ao lado",
			width=150,
			height=47,
			on_click=open_date_picker
		)

		# Função para aplicar máscara de data
		def mascara_data(e):
			valor = ''.join([c for c in data.value if c.isdigit()])
			novo_valor = ''
			if len(valor) > 0:
				novo_valor += valor[:2]
			if len(valor) > 2:
				novo_valor += '/' + valor[2:4]
			if len(valor) > 4:
				novo_valor += '/' + valor[4:8]
			data.value = novo_valor
			# Se a data estiver completa e válida, consulta o banco e atualiza
			if is_valid_ddmmyyyy(novo_valor):
				query_date = ddmmyyyy_to_yyyymmdd(novo_valor)
				if query_date:
					equipe_result = db.get_equipe_by_data(query_date) or ""
					nonlocal weekday, equipe
					# Converter para objeto date e obter nome do dia da semana
					try:
						_date_obj = datetime.strptime(novo_valor, "%d/%m/%Y").date()
						weekday = pt_weekdays[_date_obj.weekday()]
					except Exception:
						weekday = ""
					equipe = equipe_result
					team_text.value = f"{weekday} - Equipe {equipe}"
					# Atualizar dia da semana para o PDF
					atualizar_dia_semana()
					# Atualiza a tabela dinâmica
					try:
						refresh_tabela_para_data_atual()
					except Exception:
						pass
			e.control.page.update()

		data = ft.TextField(
			label="Data", 
			width=btn_data.width, 
			hint_text="dd/mm/aaaa", 
			bgcolor=ft.Colors.WHITE
		)
		data.on_change = mascara_data

		team_text = ft.Text(
			value=f"{weekday} - Equipe {equipe}",
			size=14,
			weight=ft.FontWeight.BOLD,

		)

		cont_team_text = ft.Container(
			content=team_text,
			bgcolor=ft.Colors.WHITE,
			width=btn_data.width,
			height=btn_data.height,
			alignment=ft.alignment.center,
			border_radius=4,
			border=ft.border.all(1, ft.Colors.BLACK)
		)

		def left_arrow(e):
			"""Subtrai um dia da data atual"""
			try:
				print("[LeftArrow] Subtraindo um dia da data atual")

				if not data.value or len(data.value) != 10:
					print("[LeftArrow] Erro: Data inválida")
					return

				# Converter data atual para objeto datetime
				from datetime import datetime, timedelta
				try:
					# Converter dd/mm/yyyy para datetime
					data_atual = datetime.strptime(data.value, "%d/%m/%Y")
					# Subtrair um dia
					nova_data = data_atual - timedelta(days=1)
					# Converter de volta para dd/mm/yyyy
					nova_data_str = nova_data.strftime("%d/%m/%Y")

					print(f"[LeftArrow] Data alterada de {data.value} para {nova_data_str}")

					# Atualizar o campo de data
					data.value = nova_data_str

					# Simular evento para disparar on_change (mascara_data)
					class FakeEvent:
						def __init__(self, control, page):
							self.control = control
							self.control.page = page

					# Obter page de forma mais robusta
					page_ref = None
					if hasattr(e, 'page') and e.page:
						page_ref = e.page
					elif hasattr(e, 'control') and hasattr(e.control, 'page') and e.control.page:
						page_ref = e.control.page
					elif self.page:
						page_ref = self.page

					if page_ref:
						fake_event = FakeEvent(data, page_ref)

						# Chamar a função mascara_data que é o on_change do TextField
						try:
							mascara_data(fake_event)
							print(f"[LeftArrow] Evento on_change disparado com sucesso")
						except Exception as change_ex:
							print(f"[LeftArrow] Erro ao disparar on_change: {change_ex}")
							# Fallback: atualizar manualmente
							page_ref.update()
					else:
						print(f"[LeftArrow] Erro: Não foi possível obter page para disparar on_change")

				except ValueError as ve:
					print(f"[LeftArrow] Erro ao converter data: {ve}")

			except Exception as ex:
				print(f"[LeftArrow] Erro: {ex}")
				import traceback
				traceback.print_exc()

		def right_arrow(e):
			"""Adiciona um dia à data atual"""
			try:
				print("[RightArrow] Adicionando um dia à data atual")

				if not data.value or len(data.value) != 10:
					print("[RightArrow] Erro: Data inválida")
					return

				# Converter data atual para objeto datetime
				from datetime import datetime, timedelta
				try:
					# Converter dd/mm/yyyy para datetime
					data_atual = datetime.strptime(data.value, "%d/%m/%Y")
					# Adicionar um dia
					nova_data = data_atual + timedelta(days=1)
					# Converter de volta para dd/mm/yyyy
					nova_data_str = nova_data.strftime("%d/%m/%Y")

					print(f"[RightArrow] Data alterada de {data.value} para {nova_data_str}")

					# Atualizar o campo de data
					data.value = nova_data_str

					# Simular evento para disparar on_change (mascara_data)
					class FakeEvent:
						def __init__(self, control, page):
							self.control = control
							self.control.page = page

					# Obter page de forma mais robusta
					page_ref = None
					if hasattr(e, 'page') and e.page:
						page_ref = e.page
					elif hasattr(e, 'control') and hasattr(e.control, 'page') and e.control.page:
						page_ref = e.control.page
					elif self.page:
						page_ref = self.page

					if page_ref:
						fake_event = FakeEvent(data, page_ref)

						# Chamar a função mascara_data que é o on_change do TextField
						try:
							mascara_data(fake_event)
							print(f"[RightArrow] Evento on_change disparado com sucesso")
						except Exception as change_ex:
							print(f"[RightArrow] Erro ao disparar on_change: {change_ex}")
							# Fallback: atualizar manualmente
							page_ref.update()
					else:
						print(f"[RightArrow] Erro: Não foi possível obter page para disparar on_change")

				except ValueError as ve:
					print(f"[RightArrow] Erro ao converter data: {ve}")

			except Exception as ex:
				print(f"[RightArrow] Erro: {ex}")
				import traceback
				traceback.print_exc()

		arrow_left = ft.IconButton(icon=ft.Icons.ARROW_CIRCLE_LEFT_OUTLINED,
								   icon_color=ft.Colors.BLACK,
								   on_click=left_arrow,
								   icon_size=50,
								   tooltip="Ir para dia anterior"
								   )

		arrow_right = ft.IconButton(icon=ft.Icons.ARROW_CIRCLE_RIGHT_OUTLINED,
									icon_color=ft.Colors.BLACK,
									on_click=right_arrow,
									icon_size=arrow_left.icon_size,
									tooltip="Ir para dia seguinte")

		row1 = ft.Row(
			controls=[arrow_left, btn_data, data, cont_team_text, arrow_right],
			spacing=20,
			alignment=ft.MainAxisAlignment.CENTER
		)

		# Inicializa com a data de hoje e atualiza equipe/weekday (nome do dia)
		try:
			today = datetime.now().date()
			weekday = pt_weekdays[today.weekday()]
			data.value = today.strftime("%d/%m/%Y")
			query_date = today.strftime("%Y-%m-%d")
			equipe = db.get_equipe_by_data(query_date) or ""
			team_text.value = f"{weekday} - Equipe {equipe}"
			# Atualizar dia da semana para o PDF
			atualizar_dia_semana()
			print(f"[Inicialização] Data: {data.value}, Equipe: {equipe}, Dia: {weekday}")
		except Exception as ex:
			print(f"[Inicialização] Erro: {ex}")

		btn_save = ft.ElevatedButton(
			text="Salvar",
			icon=ft.Icons.SAVE,
			width=150,
			bgcolor=ft.Colors.WHITE,
			style=ft.ButtonStyle(
				color=ft.Colors.GREEN,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.GREEN),
			),
			tooltip="Salva a escala no banco de dados",
			on_click=salvar_escala
		)

		btn_delete = ft.ElevatedButton(
			text="Deletar",
			icon=ft.Icons.DELETE,
			width=btn_save.width,
			bgcolor=ft.Colors.WHITE,
			style=ft.ButtonStyle(
				color=ft.Colors.RED,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.RED),
			),
			tooltip="Exclui a escala do bando de dados",
			on_click=deletar_escala
		)

		btn_export = ft.ElevatedButton(
			text="Exportar PDF",
			icon=ft.Icons.PICTURE_AS_PDF,
			width=btn_save.width,
			bgcolor=ft.Colors.WHITE,
			style=ft.ButtonStyle(
				color=ft.Colors.BLACK,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.BLACK),
			),
			tooltip="Gera a escala em PDF",
			on_click=exportar_pdf
		)

		row2 = ft.Row(
			controls=[btn_save, btn_delete, btn_export],
			spacing=20,
			alignment=ft.MainAxisAlignment.CENTER
		)

		# ---------------- Tabela dinâmica (colunas arrastáveis) ----------------
		# Estruturas de dados para itens em cada coluna
		col_titles = [
			"Acesso 01", "Acesso 02", "Acesso 03", "OBLL", "Férias", "Licenças", "Ausências"
		]
		col_keys = ["col1", "col2", "col3", "col4", "col5", "col6", "col7"]
		col_items = {key: [] for key in col_keys}
		# Mapeia item_id (draggable) -> dados do policial {id, nome, qra}
		id_map: dict[str, dict] = {}

		# Limpa todas as colunas
		def clear_all_columns():
			for key in col_keys:
				col_items[key].clear()
			# zera mapeamento de ids
			id_map.clear()
			update_columns()

		# Contêiner base de cada coluna
		def make_column_container(title: str):
			return ft.Container(
				content=ft.Column(
					controls=[
						ft.Text(title, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
					],
					spacing=8,
					horizontal_alignment=ft.CrossAxisAlignment.CENTER,
					expand=True,
				),
				bgcolor=ft.Colors.GREY_200,
				padding=10,
				border_radius=8,
				width=160,
				height=480,
			)

		# Drag handlers
		def drag_will_accept(e):
			e.control.content.border = ft.border.all(2, ft.Colors.BLACK45 if e.data == "true" else ft.Colors.RED)
			e.control.update()

		def drag_leave(e):
			e.control.content.border = None
			e.control.update()

		def drag_accept(e):
			src = e.page.get_control(e.src_id)
			# Encontrar item e coluna de origem
			moved = None
			src_key = None
			for key in col_keys:
				for it in list(col_items[key]):
					if getattr(it, "data", None) == getattr(src, "data", None):
						moved = it
						src_key = key
						break
				if moved:
					break
			if moved and src_key:
				col_items[src_key].remove(moved)
				target_key = e.control.data
				if target_key in col_items:
					col_items[target_key].append(moved)
				update_columns()
				# Atualiza a página após mover entre colunas
				try:
					e.page.update()
				except Exception:
					pass
			e.control.content.border = None
			e.control.update()

		# Cria Draggable para um policial com cor específica por tipo
		def make_draggable_policial(policial: dict, tipo: str = "padrao") -> ft.Draggable:
			label = policial.get("qra") or policial.get("nome") or "POL"
			item_id = str(uuid.uuid4())
			# registra mapeamento para consultas futuras (férias, etc.)
			try:
				id_map[item_id] = {
					"id": policial.get("id"),
					"nome": policial.get("nome"),
					"qra": policial.get("qra"),
					"tipo": tipo,
					"data_compensacao": policial.get("data_compensacao"),  # Para compensações
					"data_a_compensar": policial.get("data_a_compensar"),  # Para compensações
					"processo": policial.get("processo"),  # Para TACs
				}
			except Exception:
				pass
			# Define cor baseada no tipo
			cores = {
				"padrao": ft.Colors.LIGHT_GREEN,  # Verde claro - adição padrão inicial
				"obll": ft.Colors.INDIGO_200,  # Amarelo - OBLL
				"ferias": ft.Colors.BLUE_GREY_300,  # Azul acinzentado - Férias
				"licencas": ft.Colors.ORANGE,  # Laranja - Licenças
				"ausencias": ft.Colors.WHITE,  # Branco - Ausências (não licenças)
				"compensacao": ft.Colors.BROWN_200,  # Marrom claro - Compensações
				"permuta": ft.Colors.GREY_400,  # Cinza - Permutas
				"extra_diurno": ft.Colors.BLUE_200,  # Azul - Extra Diurno
				"extra_noturno": ft.Colors.YELLOW,  # Índigo - Extra Noturno
				"tac": ft.Colors.BLACK,  # Preto - TAC
			}
			bgcolor = cores.get(tipo, ft.Colors.LIGHT_GREEN)

			# Cor do texto: branco para TAC (fundo preto), preto para os demais
			text_color = ft.Colors.WHITE if tipo == "tac" else ft.Colors.BLACK

			return ft.Draggable(
				group="policiais",
				data=item_id,
				content=ft.Container(
					content=ft.Text(label, size=12, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD,
									color=text_color),
					bgcolor=bgcolor,
					padding=8,
					border_radius=6,
					alignment=ft.alignment.center,
					data=item_id,
				),
				content_feedback=ft.Container(width=20, height=20, bgcolor=bgcolor, border_radius=4),
			)

		# Atualiza UI das colunas
		def update_columns():
			for key, cont in zip(col_keys, [col1, col2, col3, col4, col5, col6, col7]):
				# mantém o título (primeiro control) e substitui os itens abaixo
				controls = cont.content.controls
				title_control = controls[0] if controls else ft.Text("")
				cont.content.controls = [title_control] + col_items[key]

		# Nota: não chamar update() aqui durante get_content; a primeira renderização cuidará disso.

		# Busca policiais elegíveis conforme regras de equipe/data
		def buscar_policiais_elegiveis(equipe_val: str, data_ddmmyyyy: str) -> list:
			if not equipe_val:
				return []
			# Converter data para objeto date
			try:
				data_sel = datetime.strptime(data_ddmmyyyy, "%d/%m/%Y").date()
			except Exception:
				return []
			# Consulta: todos NUVIG, decidimos por lógica de fase da escala (suporta dias consecutivos p/ AB/ABC)
			query = "SELECT id, nome, qra, escala, inicio, unidade FROM policiais WHERE unidade = 'NUVIG' AND IFNULL(escala, '') <> ''"
			rows = db.execute_query(query, ())
			elig = []
			for r in rows:
				escala = (r["escala"] or "").strip().upper()
				if not escala:
					continue
				# Calcular elegibilidade por fase: delta >= 0 e (delta % (4*len)) < len
				inicio_str = (r.get("inicio") if isinstance(r, dict) else r["inicio"]) if "inicio" in r.keys() else None
				if not inicio_str:
					continue
				try:
					inicio_date = datetime.strptime(inicio_str, "%Y-%m-%d").date()
				except Exception:
					continue
				delta = (data_sel - inicio_date).days
				if delta < 0:
					continue
				n = len(escala)
				period = 4 * n
				phase = delta % period
				if phase < n:
					# Hoje o policial está em serviço e a equipe do dia deve ser a letra nessa fase
					if equipe_val == escala[phase]:
						elig.append({
							"id": r["id"] if "id" in r.keys() else None,
							"nome": r["nome"] if "nome" in r.keys() else None,
							"qra": r["qra"] if "qra" in r.keys() else None,
						})
			return elig

		# Distribui policiais entre colunas Acesso 01 (até 4), Acesso 03 (até 2), restante Acesso 02
		def distribuir_policiais(policiais: list):
			# Limpa apenas colunas de acesso (mantendo outras vazias por enquanto)
			for key in ["col1", "col2", "col3"]:
				col_items[key].clear()
			# aleatório
			random.shuffle(policiais)
			# até 4 em col1
			for p in policiais[:4]:
				col_items["col1"].append(make_draggable_policial(p, "padrao"))
			# próximos 2 em col3
			for p in policiais[4:6]:
				col_items["col3"].append(make_draggable_policial(p, "padrao"))
			# restante em col2
			for p in policiais[6:]:
				col_items["col2"].append(make_draggable_policial(p, "padrao"))
			update_columns()

		# --- OBLL: buscar policiais marcados para OBLL na data ---
		def buscar_obll_para_data(data_ddmmyyyy: str) -> list:
			try:
				data_iso = ddmmyyyy_to_yyyymmdd(data_ddmmyyyy)
				if not data_iso:
					return []
				# 1) pega id da data na tabela calendario
				row_cal = db.execute_query("SELECT id FROM calendario WHERE data = ?", (data_iso,))
				if not row_cal:
					return []
				data_id = row_cal[0]["id"]
				# 2) pega policial_id na extras para operacao OBLL
				rows_extras = db.execute_query("SELECT policial_id FROM extras WHERE data_id = ? AND operacao = 'OBLL'",
											   (data_id,))
				if not rows_extras:
					return []
				pol_ids = [r["policial_id"] for r in rows_extras if "policial_id" in r.keys()]
				# 3) busca dados dos policiais
				obll_list = []
				for pid in pol_ids:
					rows_pol = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (pid,))
					if rows_pol:
						row = rows_pol[0]
						obll_list.append({
							"id": row["id"] if "id" in row.keys() else None,
							"nome": row["nome"] if "nome" in row.keys() else None,
							"qra": row["qra"] if "qra" in row.keys() else None,
						})
				return obll_list
			except Exception:
				return []

		# --- FÉRIAS: mover policiais de Acesso 01/02/03 para "Férias" quando a data cair em algum período ---
		def aplicar_ferias(data_ddmmyyyy: str):
			try:
				data_iso = ddmmyyyy_to_yyyymmdd(data_ddmmyyyy)
				if not data_iso:
					return

				# Parser auxiliar
				def parse_iso(s):
					try:
						if not s:
							return None
						return datetime.strptime(str(s).strip()[:10], "%Y-%m-%d").date()
					except Exception:
						return None

				data_sel = parse_iso(data_iso)
				if not data_sel:
					return

				# IMPORTANTE: Para efeito de Férias, considerar a escala do policial como apenas a primeira letra
				# Ou seja, se escala = "ABC", para férias ele pertence à equipe "A" durante todo o período.
				equipe_atual = (equipe or "").strip().upper()
				if not equipe_atual:
					print("[Férias] Sem equipe definida para a data; nada a aplicar.")
					return

				print(
					f"[Férias] Verificando férias para data {data_iso} ({data_sel}) considerando equipe '{equipe_atual}' pela 1ª letra da escala")

				# Buscar todos os policiais NUVIG cuja primeira letra da escala == equipe do dia
				rows_pol = db.execute_query(
					"""
					SELECT id, nome, qra
					FROM policiais
					WHERE unidade = 'NUVIG'
					  AND IFNULL(escala, '') <> ''
					  AND UPPER(SUBSTR(escala, 1, 1)) = ?
					""",
					(equipe_atual,)
				)
				pids = [r["id"] for r in rows_pol if "id" in r.keys()]
				print("[Férias] PIDs com 1ª letra da escala na equipe do dia:", pids)
				if not pids:
					update_columns()
					return

				# Consultar férias dos pids identificados
				placeholders = ",".join(["?"] * len(pids))
				rows = db.execute_query(
					f"SELECT policial_id, inicio1, fim1, inicio2, fim2, inicio3, fim3 FROM ferias WHERE policial_id IN ({placeholders})",
					tuple(pids),
				)
				print(f"[Férias] Registros ferias por policial_id: {len(rows)}")
				# Fallback: algumas bases usam matrícula na tabela ferias
				if not rows:
					mrows = db.execute_query(
						f"SELECT id, matricula FROM policiais WHERE id IN ({placeholders})",
						tuple(pids),
					)
					matriculas = [r["matricula"] for r in mrows if "matricula" in r.keys() and r["matricula"]]
					print("[Férias] Tentando fallback por matrícula:", matriculas)
					if matriculas:
						ph2 = ",".join(["?"] * len(matriculas))
						rows = db.execute_query(
							f"SELECT matricula as policial_id, inicio1, fim1, inicio2, fim2, inicio3, fim3 FROM ferias WHERE matricula IN ({ph2})",
							tuple(matriculas),
						)
						print(f"[Férias] Registros ferias por matrícula: {len(rows)}")

				# Helpers para acessar colunas de sqlite.Row com segurança
				def rg(row, key):
					try:
						return row[key]
					except Exception:
						try:
							return row.get(key)
						except Exception:
							return None

				# Verifica se data selecionada cai em algum intervalo [inicioX, fimX]
				def in_range(sel: datetime.date, ini, fim):
					di = parse_iso(ini)
					df = parse_iso(fim)
					if not di or not df:
						return False
					return di <= sel <= df

				# Identificar ids de policiais em férias hoje
				ferias_ids = set()
				for r in rows:
					pid = rg(r, "policial_id")
					if in_range(data_sel, rg(r, "inicio1"), rg(r, "fim1")) or \
							in_range(data_sel, rg(r, "inicio2"), rg(r, "fim2")) or \
							in_range(data_sel, rg(r, "inicio3"), rg(r, "fim3")):
						ferias_ids.add(pid)
						print(f"[Férias] Policial em férias na data {data_iso}: pid={pid}")

				# Conjunto de ids já presentes na coluna Férias para evitar duplicidades
				exist_ferias_ids = set()
				for it in col_items["col5"]:
					pid_exist = id_map.get(getattr(it, "data", ""), {}).get("id")
					if pid_exist:
						exist_ferias_ids.add(pid_exist)

				# 1) Remover dos acessos e mover para Férias quando necessário
				if ferias_ids:
					print("[Férias] Movendo para coluna Férias ids:", ferias_ids)
					for key in ["col1", "col2", "col3"]:
						rem = []
						for it in col_items[key]:
							pid_it = id_map.get(getattr(it, "data", ""), {}).get("id")
							if pid_it in ferias_ids:
								pinfo = id_map.get(getattr(it, "data", ""), {})
								print(f"[Férias] Removendo de {key} e adicionando em Férias:", pinfo)
								col_items["col5"].append(make_draggable_policial(pinfo, "ferias"))
								exist_ferias_ids.add(pid_it)
								rem.append(it)
						for it in rem:
							col_items[key].remove(it)

				# 2) Garantir que todos em ferias_ids apareçam na coluna Férias, mesmo se não estavam nos acessos
				faltantes = [pid for pid in ferias_ids if pid not in exist_ferias_ids]
				if faltantes:
					print("[Férias] Adicionando faltantes diretamente na coluna Férias:", faltantes)
					ph3 = ",".join(["?"] * len(faltantes))
					rows_falt = db.execute_query(
						f"SELECT id, nome, qra FROM policiais WHERE id IN ({ph3})",
						tuple(faltantes),
					)
					for row in rows_falt:
						pol_data = {
							"id": row["id"] if "id" in row.keys() else None,
							"nome": row["nome"] if "nome" in row.keys() else None,
							"qra": row["qra"] if "qra" in row.keys() else None,
						}
						col_items["col5"].append(make_draggable_policial(pol_data, "ferias"))

				update_columns()
			except Exception as ex:
				print("[Férias] Erro ao aplicar férias:", ex)
				return

		# --- LICENÇAS/AUSÊNCIAS: mover policiais de Acesso 01/02/03 para "Licenças" ou "Ausências" conforme motivo ---
		def aplicar_licencas(data_ddmmyyyy: str):
			try:
				data_iso = ddmmyyyy_to_yyyymmdd(data_ddmmyyyy)
				if not data_iso:
					return

				# Parser auxiliar
				def parse_iso(s):
					try:
						if not s:
							return None
						return datetime.strptime(str(s).strip()[:10], "%Y-%m-%d").date()
					except Exception:
						return None

				data_sel = parse_iso(data_iso)
				if not data_sel:
					return
				print(f"[Licenças/Ausências] Verificando para data {data_iso} ({data_sel})")
				# Coleta ids dos policiais nas colunas de acesso
				pids = []
				for key in ["col1", "col2", "col3"]:
					for it in col_items[key]:
						pid = id_map.get(getattr(it, "data", ""), {}).get("id")
						if pid:
							pids.append(pid)
				if not pids:
					return
				print("[Licenças/Ausências] PIDs nas colunas de acesso:", pids)
				placeholders = ",".join(["?"] * len(pids))
				rows = db.execute_query(
					f"SELECT policial_id, inicio, fim, licenca FROM licencas WHERE policial_id IN ({placeholders})",
					tuple(pids),
				)
				print(f"[Licenças/Ausências] Registros encontrados: {len(rows)}")

				# Helper para verificar range
				def in_range(sel, ini, fim):
					di = parse_iso(ini)
					df = parse_iso(fim)
					if not di or not df:
						return False
					return di <= sel <= df

				lic_ids = set()  # Para licenças (contém "licença" no motivo)
				aus_ids = set()  # Para ausências (demais motivos)
				for r in rows:
					pid = None
					try:
						pid = r["policial_id"]
					except Exception:
						pid = r.get("policial_id") if hasattr(r, "get") else None
					if in_range(data_sel, r["inicio"] if "inicio" in r.keys() else None,
								r["fim"] if "fim" in r.keys() else None):
						# Verifica se é licença ou ausência pelo campo 'licenca'
						motivo = ""
						try:
							motivo = (r["licenca"] or "").lower()
						except Exception:
							motivo = (r.get("licenca", "") or "").lower()
						if "licença" in motivo or "licenca" in motivo:
							lic_ids.add(pid)
							print(
								f"[Licenças] Policial em licença na data {data_iso}: pid={pid}, motivo='{motivo}', periodo=",
								r.get("inicio") if hasattr(r, "get") else r["inicio"],
								r.get("fim") if hasattr(r, "get") else r["fim"])
						else:
							aus_ids.add(pid)
							print(
								f"[Ausências] Policial em ausência na data {data_iso}: pid={pid}, motivo='{motivo}', periodo=",
								r.get("inicio") if hasattr(r, "get") else r["inicio"],
								r.get("fim") if hasattr(r, "get") else r["fim"])
				# Move licenças para col6
				if lic_ids:
					print("[Licenças] Movendo para coluna Licenças ids:", lic_ids)
					for key in ["col1", "col2", "col3"]:
						rem = []
						for it in col_items[key]:
							pid = id_map.get(getattr(it, "data", ""), {}).get("id")
							if pid in lic_ids:
								pinfo = id_map.get(getattr(it, "data", ""), {})
								print(f"[Licenças] Removendo de {key} e adicionando em Licenças:", pinfo)
								col_items["col6"].append(make_draggable_policial(pinfo, "licencas"))
								rem.append(it)
						for it in rem:
							col_items[key].remove(it)
				# Move ausências para col7
				if aus_ids:
					print("[Ausências] Movendo para coluna Ausências ids:", aus_ids)
					for key in ["col1", "col2", "col3"]:
						rem = []
						for it in col_items[key]:
							pid = id_map.get(getattr(it, "data", ""), {}).get("id")
							if pid in aus_ids:
								pinfo = id_map.get(getattr(it, "data", ""), {})
								print(f"[Ausências] Removendo de {key} e adicionando em Ausências:", pinfo)
								col_items["col7"].append(make_draggable_policial(pinfo, "ausencias"))
								rem.append(it)
						for it in rem:
							col_items[key].remove(it)
				update_columns()
			except Exception as ex:
				print("[Licenças/Ausências] Erro ao aplicar:", ex)
				return

		# --- COMPENSAÇÕES: buscar policiais por compensação e a_compensar ---
		def aplicar_compensacoes(data_ddmmyyyy: str):
			try:
				data_iso = ddmmyyyy_to_yyyymmdd(data_ddmmyyyy)
				if not data_iso:
					return
				print(f"[Compensações] Verificando compensações para data {data_iso}")

				# 1) Buscar policiais que devem trabalhar na data (coluna compensacao)
				rows_trabalhar = db.execute_query(
					"SELECT policial_id, compensacao, a_compensar FROM compensacoes WHERE compensacao = ?",
					(data_iso,)
				)
				print(f"[Compensações] Policiais que devem trabalhar hoje: {len(rows_trabalhar)}")

				for r in rows_trabalhar:
					pid = r["policial_id"] if "policial_id" in r.keys() else None
					if pid:
						# Buscar dados do policial
						pol_rows = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (pid,))
						if pol_rows:
							pol = pol_rows[0]
							pol_data = {
								"id": pol["id"] if "id" in pol.keys() else None,
								"nome": pol["nome"] if "nome" in pol.keys() else None,
								"qra": pol["qra"] if "qra" in pol.keys() else None,
								"data_compensacao": r["compensacao"] if "compensacao" in r.keys() else None,
								"data_a_compensar": r["a_compensar"] if "a_compensar" in r.keys() else None,
							}
							# Distribuir entre acessos (similar à distribuição padrão)
							# Prioridade: col1 (até 4), col3 (até 2), col2 (restante)
							compensacao_item = make_draggable_policial(pol_data, "compensacao")
							if len(col_items["col1"]) < 4:
								col_items["col1"].append(compensacao_item)
							elif len(col_items["col3"]) < 2:
								col_items["col3"].append(compensacao_item)
							else:
								col_items["col2"].append(compensacao_item)
							
							# Armazenar informação de compensação no id_map (trabalha hoje, compensa outro dia)
							comp_key = getattr(compensacao_item, "data", "")
							print(f"[DEBUG COMPENSACAO] Armazenando info para compensacao key: {comp_key}")
							if comp_key in id_map:
								# Converter data_a_compensar para formato dd/mm/yyyy
								data_a_compensar_br = yyyymmdd_to_ddmmyyyy(pol_data.get('data_a_compensar', ''))
								id_map[comp_key]["compensacao_info"] = {
									"tipo": "trabalha",
									"data_compensada": data_a_compensar_br
								}
								print(f"[DEBUG COMPENSACAO] Info armazenada para {pol_data.get('qra')}: {id_map[comp_key]['compensacao_info']}")
							else:
								print(f"[DEBUG COMPENSACAO] Key {comp_key} não encontrada no id_map")
							
							print(
								f"[Compensações] Adicionado aos acessos: {pol_data.get('qra') or pol_data.get('nome')}")

				# 2) Buscar policiais que devem compensar na data (coluna a_compensar)
				rows_compensar = db.execute_query(
					"SELECT policial_id, compensacao, a_compensar FROM compensacoes WHERE a_compensar = ?",
					(data_iso,)
				)
				print(f"[Compensações] Policiais que devem compensar hoje: {len(rows_compensar)}")

				# Coletar IDs dos policiais que devem compensar
				compensar_ids = set()
				for r in rows_compensar:
					pid = r["policial_id"] if "policial_id" in r.keys() else None
					if pid:
						compensar_ids.add(pid)

				# Remover dos acessos os policiais que devem compensar
				if compensar_ids:
					print(f"[Compensações] Removendo dos acessos policiais que devem compensar: {compensar_ids}")
					for key in ["col1", "col2", "col3"]:
						rem = []
						for it in col_items[key]:
							pid = id_map.get(getattr(it, "data", ""), {}).get("id")
							if pid in compensar_ids:
								rem.append(it)
								print(
									f"[Compensações] Removendo de {key}: {id_map.get(getattr(it, 'data', ''), {}).get('qra') or id_map.get(getattr(it, 'data', ''), {}).get('nome')}")
						for it in rem:
							col_items[key].remove(it)

				# Adicionar à coluna Ausências
				for r in rows_compensar:
					pid = r["policial_id"] if "policial_id" in r.keys() else None
					if pid:
						# Buscar dados do policial
						pol_rows = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (pid,))
						if pol_rows:
							pol = pol_rows[0]
							pol_data = {
								"id": pol["id"] if "id" in pol.keys() else None,
								"nome": pol["nome"] if "nome" in pol.keys() else None,
								"qra": pol["qra"] if "qra" in pol.keys() else None,
								"data_compensacao": r["compensacao"] if "compensacao" in r.keys() else None,
								"data_a_compensar": r["a_compensar"] if "a_compensar" in r.keys() else None,
							}
							# Adicionar à coluna Ausências
							ausencia_item = make_draggable_policial(pol_data, "compensacao")
							col_items["col7"].append(ausencia_item)
							
							# Armazenar informação de compensação no id_map (ausente hoje, trabalhou outro dia)
							aus_key = getattr(ausencia_item, "data", "")
							print(f"[DEBUG COMPENSACAO] Armazenando info para ausencia key: {aus_key}")
							if aus_key in id_map:
								# Converter data_compensacao para formato dd/mm/yyyy
								data_compensacao_br = yyyymmdd_to_ddmmyyyy(pol_data.get('data_compensacao', ''))
								id_map[aus_key]["compensacao_info"] = {
									"tipo": "ausente",
									"data_trabalhada": data_compensacao_br
								}
								print(f"[DEBUG COMPENSACAO] Info armazenada para {pol_data.get('qra')}: {id_map[aus_key]['compensacao_info']}")
							else:
								print(f"[DEBUG COMPENSACAO] Key {aus_key} não encontrada no id_map")
							
							print(
								f"[Compensações] Adicionado às ausências: {pol_data.get('qra') or pol_data.get('nome')}")

				update_columns()
			except Exception as ex:
				print("[Compensações] Erro ao aplicar compensações:", ex)
				return

		# --- PERMUTAS: buscar e aplicar permutas por data_solicitante e data_permutado ---
		def aplicar_permutas(data_ddmmyyyy: str):
			try:
				data_iso = ddmmyyyy_to_yyyymmdd(data_ddmmyyyy)
				if not data_iso:
					return
				print(f"[Permutas] Verificando permutas para data {data_iso}")

				# Dicionários para armazenar dados das permutas
				permutas_solicitante = {}
				permutas_permutado = {}

				# 1) Buscar permutas onde data_solicitante = data selecionada
				rows_solicitante = db.execute_query(
					"SELECT solicitante, permutado, data_solicitante, data_permutado FROM permutas WHERE data_solicitante = ?",
					(data_iso,)
				)
				print(f"[Permutas] Permutas por data_solicitante: {len(rows_solicitante)}")

				for r in rows_solicitante:
					solicitante_id = r["solicitante"] if "solicitante" in r.keys() else None
					permutado_id = r["permutado"] if "permutado" in r.keys() else None
					data_solicitante = r["data_solicitante"] if "data_solicitante" in r.keys() else None
					data_permutado = r["data_permutado"] if "data_permutado" in r.keys() else None

					if solicitante_id and permutado_id:
						# Armazenar dados da permuta
						permuta_key = f"{solicitante_id}_{permutado_id}_{data_solicitante}"
						permutas_solicitante[permuta_key] = {
							"solicitante_id": solicitante_id,
							"permutado_id": permutado_id,
							"data_solicitante": data_solicitante,
							"data_permutado": data_permutado,
							"tipo": "solicitante_sai"
						}

						# Remover solicitante dos acessos e mover para ausências
						_processar_permuta_solicitante_sai(solicitante_id, permutado_id)

				# 2) Buscar permutas onde data_permutado = data selecionada
				rows_permutado = db.execute_query(
					"SELECT solicitante, permutado, data_solicitante, data_permutado FROM permutas WHERE data_permutado = ?",
					(data_iso,)
				)
				print(f"[Permutas] Permutas por data_permutado: {len(rows_permutado)}")

				for r in rows_permutado:
					solicitante_id = r["solicitante"] if "solicitante" in r.keys() else None
					permutado_id = r["permutado"] if "permutado" in r.keys() else None
					data_solicitante = r["data_solicitante"] if "data_solicitante" in r.keys() else None
					data_permutado = r["data_permutado"] if "data_permutado" in r.keys() else None

					if solicitante_id and permutado_id:
						# Armazenar dados da permuta
						permuta_key = f"{solicitante_id}_{permutado_id}_{data_permutado}"
						permutas_permutado[permuta_key] = {
							"solicitante_id": solicitante_id,
							"permutado_id": permutado_id,
							"data_solicitante": data_solicitante,
							"data_permutado": data_permutado,
							"tipo": "permutado_sai"
						}

						# Remover permutado dos acessos e mover para ausências
						_processar_permuta_permutado_sai(solicitante_id, permutado_id)

				# Imprimir dicionários no console
				print(f"O dicionário permutas_solicitante é: {permutas_solicitante}")
				print(f"O dicionário permutas_permutado é: {permutas_permutado}")

				update_columns()
			except Exception as ex:
				print("[Permutas] Erro ao aplicar permutas:", ex)
				return

		def _processar_permuta_solicitante_sai(solicitante_id: int, permutado_id: int):
			"""Processa permuta quando solicitante deve sair (data_solicitante = data selecionada)"""
			# Buscar dados dos policiais
			sol_rows = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (solicitante_id,))
			perm_rows = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (permutado_id,))

			if not sol_rows or not perm_rows:
				return

			solicitante_data = {
				"id": sol_rows[0]["id"] if "id" in sol_rows[0].keys() else None,
				"nome": sol_rows[0]["nome"] if "nome" in sol_rows[0].keys() else None,
				"qra": sol_rows[0]["qra"] if "qra" in sol_rows[0].keys() else None,
			}

			permutado_data = {
				"id": perm_rows[0]["id"] if "id" in perm_rows[0].keys() else None,
				"nome": perm_rows[0]["nome"] if "nome" in perm_rows[0].keys() else None,
				"qra": perm_rows[0]["qra"] if "qra" in perm_rows[0].keys() else None,
			}

			# Remover solicitante dos acessos
			for key in ["col1", "col2", "col3"]:
				rem = []
				for it in col_items[key]:
					pid = id_map.get(getattr(it, "data", ""), {}).get("id")
					if pid == solicitante_id:
						rem.append(it)
						print(
							f"[Permutas] Removendo solicitante de {key}: {solicitante_data.get('qra') or solicitante_data.get('nome')}")
				for it in rem:
					col_items[key].remove(it)

			# Adicionar solicitante às ausências
			solicitante_item = make_draggable_policial(solicitante_data, "permuta")
			col_items["col7"].append(solicitante_item)
			
			# Armazenar informação de permuta no id_map para o solicitante (sai)
			solicitante_key = getattr(solicitante_item, "data", "")
			print(f"[DEBUG PERMUTA] Armazenando info para solicitante key: {solicitante_key}")
			if solicitante_key in id_map:
				id_map[solicitante_key]["permuta_info"] = {
					"tipo": "sai",
					"com": permutado_data.get('qra') or permutado_data.get('nome')
				}
				print(f"[DEBUG PERMUTA] Info armazenada para {solicitante_data.get('qra')}: {id_map[solicitante_key]['permuta_info']}")
			else:
				print(f"[DEBUG PERMUTA] Key {solicitante_key} não encontrada no id_map")
			
			print(
				f"[Permutas] Solicitante adicionado às ausências: {solicitante_data.get('qra') or solicitante_data.get('nome')}")

			# Adicionar permutado aos acessos
			permutado_item = make_draggable_policial(permutado_data, "permuta")
			if len(col_items["col1"]) < 4:
				col_items["col1"].append(permutado_item)
			elif len(col_items["col3"]) < 2:
				col_items["col3"].append(permutado_item)
			else:
				col_items["col2"].append(permutado_item)
			
			# Armazenar informação de permuta no id_map para o permutado (entra)
			permutado_key = getattr(permutado_item, "data", "")
			print(f"[DEBUG PERMUTA] Armazenando info para permutado key: {permutado_key}")
			if permutado_key in id_map:
				id_map[permutado_key]["permuta_info"] = {
					"tipo": "entra",
					"com": solicitante_data.get('qra') or solicitante_data.get('nome')
				}
				print(f"[DEBUG PERMUTA] Info armazenada para {permutado_data.get('qra')}: {id_map[permutado_key]['permuta_info']}")
			else:
				print(f"[DEBUG PERMUTA] Key {permutado_key} não encontrada no id_map")
			
			print(
				f"[Permutas] Permutado adicionado aos acessos: {permutado_data.get('qra') or permutado_data.get('nome')}")

		def _processar_permuta_permutado_sai(solicitante_id: int, permutado_id: int):
			"""Processa permuta quando permutado deve sair (data_permutado = data selecionada)"""
			# Buscar dados dos policiais
			sol_rows = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (solicitante_id,))
			perm_rows = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (permutado_id,))

			if not sol_rows or not perm_rows:
				return

			solicitante_data = {
				"id": sol_rows[0]["id"] if "id" in sol_rows[0].keys() else None,
				"nome": sol_rows[0]["nome"] if "nome" in sol_rows[0].keys() else None,
				"qra": sol_rows[0]["qra"] if "qra" in sol_rows[0].keys() else None,
			}

			permutado_data = {
				"id": perm_rows[0]["id"] if "id" in perm_rows[0].keys() else None,
				"nome": perm_rows[0]["nome"] if "nome" in perm_rows[0].keys() else None,
				"qra": perm_rows[0]["qra"] if "qra" in perm_rows[0].keys() else None,
			}

			# Remover permutado dos acessos
			for key in ["col1", "col2", "col3"]:
				rem = []
				for it in col_items[key]:
					pid = id_map.get(getattr(it, "data", ""), {}).get("id")
					if pid == permutado_id:
						rem.append(it)
						print(
							f"[Permutas] Removendo permutado de {key}: {permutado_data.get('qra') or permutado_data.get('nome')}")
				for it in rem:
					col_items[key].remove(it)

			# Adicionar permutado às ausências
			permutado_item = make_draggable_policial(permutado_data, "permuta")
			col_items["col7"].append(permutado_item)
			
			# Armazenar informação de permuta no id_map para o permutado (sai)
			permutado_key = getattr(permutado_item, "data", "")
			print(f"[DEBUG PERMUTA] Armazenando info para permutado key: {permutado_key}")
			if permutado_key in id_map:
				id_map[permutado_key]["permuta_info"] = {
					"tipo": "sai",
					"com": solicitante_data.get('qra') or solicitante_data.get('nome')
				}
				print(f"[DEBUG PERMUTA] Info armazenada para {permutado_data.get('qra')}: {id_map[permutado_key]['permuta_info']}")
			else:
				print(f"[DEBUG PERMUTA] Key {permutado_key} não encontrada no id_map")
			
			print(
				f"[Permutas] Permutado adicionado às ausências: {permutado_data.get('qra') or permutado_data.get('nome')}")

			# Adicionar solicitante aos acessos
			solicitante_item = make_draggable_policial(solicitante_data, "permuta")
			if len(col_items["col1"]) < 4:
				col_items["col1"].append(solicitante_item)
			elif len(col_items["col3"]) < 2:
				col_items["col3"].append(solicitante_item)
			else:
				col_items["col2"].append(solicitante_item)
			
			# Armazenar informação de permuta no id_map para o solicitante (entra)
			solicitante_key = getattr(solicitante_item, "data", "")
			print(f"[DEBUG PERMUTA] Armazenando info para solicitante key: {solicitante_key}")
			if solicitante_key in id_map:
				id_map[solicitante_key]["permuta_info"] = {
					"tipo": "entra",
					"com": permutado_data.get('qra') or permutado_data.get('nome')
				}
				print(f"[DEBUG PERMUTA] Info armazenada para {solicitante_data.get('qra')}: {id_map[solicitante_key]['permuta_info']}")
			else:
				print(f"[DEBUG PERMUTA] Key {solicitante_key} não encontrada no id_map")
			
			print(
				f"[Permutas] Solicitante adicionado aos acessos: {solicitante_data.get('qra') or solicitante_data.get('nome')}")

		# --- EXTRAS: buscar policiais de extra para operação "Rotina" na data ---
		def aplicar_extras(data_ddmmyyyy: str):
			try:
				data_iso = ddmmyyyy_to_yyyymmdd(data_ddmmyyyy)
				if not data_iso:
					return
				print(f"[Extras] Verificando extras para data {data_iso}")

				# Buscar extras com operação "Rotina" na data selecionada
				rows = db.execute_query(
					"SELECT policial_id, turno FROM extras WHERE data_id = (SELECT id FROM calendario WHERE data = ?) AND operacao = 'Rotina'",
					(data_iso,)
				)
				print(f"[Extras] Extras encontrados para Rotina: {len(rows)}")

				for r in rows:
					policial_id = r["policial_id"] if "policial_id" in r.keys() else None
					turno = (r["turno"] if "turno" in r.keys() else "").strip().lower()

					if policial_id:
						# Buscar dados do policial
						pol_rows = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (policial_id,))
						if pol_rows:
							pol = pol_rows[0]
							pol_data = {
								"id": pol["id"] if "id" in pol.keys() else None,
								"nome": pol["nome"] if "nome" in pol.keys() else None,
								"qra": pol["qra"] if "qra" in pol.keys() else None,
								"turno": turno,
							}

							# Determinar tipo baseado no turno
							if turno == "diurno":
								tipo = "extra_diurno"
								print(f"[Extras] Extra Diurno: {pol_data.get('qra') or pol_data.get('nome')}")
							elif turno == "noturno":
								tipo = "extra_noturno"
								print(f"[Extras] Extra Noturno: {pol_data.get('qra') or pol_data.get('nome')}")
							else:
								tipo = "extra_diurno"  # Default para diurno se não especificado
								print(
									f"[Extras] Extra (turno indefinido, assumindo diurno): {pol_data.get('qra') or pol_data.get('nome')}")

							# Distribuir entre acessos (similar à distribuição padrão)
							# Prioridade: col1 (até 4), col3 (até 2), col2 (restante)
							if len(col_items["col1"]) < 4:
								col_items["col1"].append(make_draggable_policial(pol_data, tipo))
							elif len(col_items["col3"]) < 2:
								col_items["col3"].append(make_draggable_policial(pol_data, tipo))
							else:
								col_items["col2"].append(make_draggable_policial(pol_data, tipo))

							print(
								f"[Extras] Adicionado aos acessos: {pol_data.get('qra') or pol_data.get('nome')} ({turno})")

				update_columns()
			except Exception as ex:
				print("[Extras] Erro ao aplicar extras:", ex)
				return

		# --- TACs: buscar policiais com TAC na data e adicionar aos acessos ---
		def aplicar_tacs(data_ddmmyyyy: str):
			try:
				data_iso = ddmmyyyy_to_yyyymmdd(data_ddmmyyyy)
				if not data_iso:
					return
				print(f"[TACs] Verificando TACs para data {data_iso}")

				# Buscar TACs na data selecionada
				rows = db.execute_query(
					"SELECT policial_id, processo FROM tacs WHERE date(data) = date(?)",
					(data_iso,)
				)
				print(f"[TACs] TACs encontrados: {len(rows)}")

				for r in rows:
					policial_id = r["policial_id"] if "policial_id" in r.keys() else None
					processo = r["processo"] if "processo" in r.keys() else ""

					if policial_id:
						# Buscar dados do policial
						pol_rows = db.execute_query("SELECT id, nome, qra FROM policiais WHERE id = ?", (policial_id,))
						if pol_rows:
							pol = pol_rows[0]
							pol_data = {
								"id": pol["id"] if "id" in pol.keys() else None,
								"nome": pol["nome"] if "nome" in pol.keys() else None,
								"qra": pol["qra"] if "qra" in pol.keys() else None,
								"processo": processo,  # Armazenar processo para uso futuro
							}

							print(
								f"[TACs] TAC encontrado: {pol_data.get('qra') or pol_data.get('nome')} - Processo: {processo}")

							# Distribuir entre acessos (similar à distribuição padrão)
							# Prioridade: col1 (até 4), col3 (até 2), col2 (restante)
							tac_item = make_draggable_policial(pol_data, "tac")
							if len(col_items["col1"]) < 4:
								col_items["col1"].append(tac_item)
							elif len(col_items["col3"]) < 2:
								col_items["col3"].append(tac_item)
							else:
								col_items["col2"].append(tac_item)

							# Armazenar informação de TAC no id_map
							tac_key = getattr(tac_item, "data", "")
							print(f"[DEBUG TAC] Armazenando info para TAC key: {tac_key}")
							if tac_key in id_map:
								id_map[tac_key]["tac_info"] = {
									"processo": processo
								}
								print(f"[DEBUG TAC] Info armazenada para {pol_data.get('qra')}: {id_map[tac_key]['tac_info']}")
							else:
								print(f"[DEBUG TAC] Key {tac_key} não encontrada no id_map")

							print(
								f"[TACs] Adicionado aos acessos: {pol_data.get('qra') or pol_data.get('nome')} (Processo: {processo})")

				update_columns()
			except Exception as ex:
				print("[TACs] Erro ao aplicar TACs:", ex)
				return

		def preencher_coluna_obll(data_ddmmyyyy: str):
			# limpa somente a coluna OBLL (col4)
			col_items["col4"].clear()
			obll = buscar_obll_para_data(data_ddmmyyyy)
			for p in obll:
				col_items["col4"].append(make_draggable_policial(p, "obll"))
			update_columns()

		# Monta as 7 colunas com títulos e DragTargets
		col1 = make_column_container(col_titles[0])
		col2 = make_column_container(col_titles[1])
		col3 = make_column_container(col_titles[2])
		col4 = make_column_container(col_titles[3])
		col5 = make_column_container(col_titles[4])
		col6 = make_column_container(col_titles[5])
		col7 = make_column_container(col_titles[6])

		col1_drag = ft.DragTarget(group="policiais", content=col1, on_will_accept=drag_will_accept,
								  on_accept=drag_accept, on_leave=drag_leave, data="col1")
		col2_drag = ft.DragTarget(group="policiais", content=col2, on_will_accept=drag_will_accept,
								  on_accept=drag_accept, on_leave=drag_leave, data="col2")
		col3_drag = ft.DragTarget(group="policiais", content=col3, on_will_accept=drag_will_accept,
								  on_accept=drag_accept, on_leave=drag_leave, data="col3")
		col4_drag = ft.DragTarget(group="policiais", content=col4, on_will_accept=drag_will_accept,
								  on_accept=drag_accept, on_leave=drag_leave, data="col4")
		col5_drag = ft.DragTarget(group="policiais", content=col5, on_will_accept=drag_will_accept,
								  on_accept=drag_accept, on_leave=drag_leave, data="col5")
		col6_drag = ft.DragTarget(group="policiais", content=col6, on_will_accept=drag_will_accept,
								  on_accept=drag_accept, on_leave=drag_leave, data="col6")
		col7_drag = ft.DragTarget(group="policiais", content=col7, on_will_accept=drag_will_accept,
								  on_accept=drag_accept, on_leave=drag_leave, data="col7")

		container_tabela_dinamica = ft.Container(
			width=1200,
			height=500,
			bgcolor=ft.Colors.WHITE,
			padding=10,
			border_radius=8,
			content=ft.Row(
				controls=[col1_drag, col2_drag, col3_drag, col4_drag, col5_drag, col6_drag, col7_drag],
				spacing=10,
				alignment=ft.MainAxisAlignment.SPACE_AROUND,
				expand=True,
			),
		)

		# Função para atualizar a escala do dia na tabela (chamar quando equipe/data mudarem)
		def carregar_escala_salva(data_ddmmyyyy: str) -> bool:
			"""Tenta carregar escala salva do banco. Retorna True se carregou, False se não encontrou."""
			try:
				data_iso = ddmmyyyy_to_yyyymmdd(data_ddmmyyyy)
				if not data_iso:
					return False

				print(f"[Carregar] Verificando se existe escala salva para {data_iso}")

				# Buscar escala salva no banco
				rows = db.execute_query("SELECT escala FROM calendario WHERE data = ?", (data_iso,))

				if not rows or len(rows) == 0:
					print(f"[Carregar] Nenhuma escala encontrada para {data_iso}")
					return False

				escala_json = None
				try:
					row = rows[0]
					escala_json = row['escala'] if 'escala' in row.keys() else row[0]
				except:
					row = rows[0]
					escala_json = row[0]

				if not escala_json:
					print(f"[Carregar] Coluna escala está vazia para {data_iso}")
					return False

				print(f"[Carregar] Escala encontrada, tentando carregar JSON...")

				# Tentar fazer parse do JSON
				import json
				try:
					dados_escala = json.loads(escala_json)
					print(f"[Carregar] JSON válido encontrado, carregando escala...")
				except json.JSONDecodeError as je:
					print(f"[Carregar] JSON inválido: {je}")
					return False

				# Limpar colunas antes de carregar
				clear_all_columns()

				# Mapear status para tipos
				status_para_tipo = {
					"Plantão": "padrao",
					"OBLL": "obll",
					"Férias": "ferias",
					"Licença": "licencas",
					"Ausência": "ausencias",
					"Compensação": "compensacao",
					"Permuta": "permuta",
					"Extra diurno": "extra_diurno",
					"Extra noturno": "extra_noturno",
					"TAC": "tac"
				}

				# Mapear nomes das colunas para chaves
				col_name_to_key = {
					"Acesso 01": "col1",
					"Acesso 02": "col2",
					"Acesso 03": "col3",
					"OBLL": "col4",
					"Férias": "col5",
					"Licenças": "col6",
					"Ausências": "col7"
				}

				# Carregar cada coluna
				for col_name, policiais in dados_escala.items():
					col_key = col_name_to_key.get(col_name)
					if not col_key:
						print(f"[Carregar] Coluna desconhecida: {col_name}")
						continue

					print(f"[Carregar] Carregando {len(policiais)} policiais na coluna {col_name}")

					for pol_data in policiais:
						nome = pol_data.get("nome", "DESCONHECIDO")
						status = pol_data.get("status", "Plantão")
						tipo = status_para_tipo.get(status, "padrao")

						# Criar dados do policial (simulando estrutura)
						policial_info = {
							"nome": nome,
							"qra": nome,  # Usando nome como QRA por enquanto
							"id": None,  # Não temos ID na escala salva
							"tipo": tipo
						}

						# Adicionar à coluna
						col_items[col_key].append(make_draggable_policial(policial_info, tipo))
						print(f"[Carregar] Adicionado {nome} ({status}) à coluna {col_name}")

				update_columns()
				print(f"[Carregar] ✓ Escala carregada com sucesso para {data_iso}")
				return True

			except Exception as ex:
				print(f"[Carregar] Erro ao carregar escala: {ex}")
				import traceback
				traceback.print_exc()
				return False

		def refresh_tabela_para_data_atual():
			if not equipe or not data.value or len(data.value) != 10:
				return

			print("[Calendario] Refresh para data:", data.value, "equipe:", equipe)

			# PRIMEIRO: Tentar carregar escala salva
			if carregar_escala_salva(data.value):
				print("[Calendario] ✓ Escala salva carregada, não gerando nova distribuição")
				try:
					if self.page:
						self.page.update()
				except Exception:
					pass
				return

			# SE NÃO ENCONTROU ESCALA SALVA: Gerar nova distribuição
			print("[Calendario] Nenhuma escala salva encontrada, gerando nova distribuição...")

			# Sempre começar limpando todas as colunas
			clear_all_columns()
			pols = buscar_policiais_elegiveis(equipe, data.value)
			print(f"[Calendario] Policiais elegíveis ({len(pols)}):", [p.get("qra") or p.get("nome") for p in pols])
			distribuir_policiais(pols)
			# Aplica compensações: adiciona aos acessos e ausências
			aplicar_compensacoes(data.value)
			# Aplica permutas: troca policiais entre acessos e ausências
			aplicar_permutas(data.value)
			# Aplica extras: adiciona aos acessos com cores por turno
			aplicar_extras(data.value)
			# Aplica TACs: adiciona aos acessos com fundo preto e letra branca
			aplicar_tacs(data.value)
			# Aplica férias e licenças: movem de acessos para colunas específicas
			aplicar_ferias(data.value)
			aplicar_licencas(data.value)
			# Preenche OBLL para a data
			preencher_coluna_obll(data.value)
			# Atualizar dia da semana para o PDF
			atualizar_dia_semana()
			try:
				if self.page:
					self.page.update()
			except Exception:
				pass

		# Atualiza tabela ao carregar e após mudanças de data/equipe
		refresh_tabela_para_data_atual()

		legenda = ft.Row(
			controls=[
				ft.Container(
					content=ft.Text(value="Legenda",
									size=14,
									weight=ft.FontWeight.BOLD,
									color=ft.Colors.BLACK,
									text_align=ft.TextAlign.CENTER),
					# bgcolor=ft.Colors.LIGHT_GREEN,
					width=120,
					alignment=ft.alignment.center,
					border_radius=4,
					border=ft.border.all(1, ft.Colors.BLACK45)
				),

				ft.Container(
					content=ft.Text(value="Plantão",
									size=12,
									weight=ft.FontWeight.BOLD,
									color=ft.Colors.BLACK,
									text_align=ft.TextAlign.CENTER),
					bgcolor=ft.Colors.LIGHT_GREEN,
					width=120,
					alignment=ft.alignment.center,
					border_radius=4,
					border=ft.border.all(1, ft.Colors.BLACK45)
				),

				ft.Container(
					content=ft.Text(value="Extra diurno",
									size=12,
									weight=ft.FontWeight.BOLD,
									color=ft.Colors.BLACK,
									text_align=ft.TextAlign.CENTER),
					bgcolor=ft.Colors.BLUE_200,
					width=120,
					alignment=ft.alignment.center,
					border_radius=4,
					border=ft.border.all(1, ft.Colors.BLACK45)
				),

				ft.Container(
					content=ft.Text(value="Extra Noturno",
									size=12,
									weight=ft.FontWeight.BOLD,
									color=ft.Colors.BLACK,
									text_align=ft.TextAlign.CENTER),
					bgcolor=ft.Colors.YELLOW,
					width=120,
					alignment=ft.alignment.center,
					border_radius=4,
					border=ft.border.all(1, ft.Colors.BLACK45)
				),

				# ft.Container(
				# 	content=ft.Text(value="OBLL",
				# 					size=12,
				# 					weight=ft.FontWeight.BOLD,
				# 					color=ft.Colors.BLACK),
				# 	bgcolor=ft.Colors.YELLOW,
				# 	width=120,
				# 	alignment=ft.alignment.center,
				# 	border_radius=4,
				# 	border=ft.border.all(1, ft.Colors.BLACK45)
				# ),
				#
				# ft.Container(
				# 	content=ft.Text(value="Licenças",
				# 					size=12,
				# 					weight=ft.FontWeight.BOLD,
				# 					color=ft.Colors.BLACK),
				# 	bgcolor=ft.Colors.ORANGE,
				# 	width=120,
				# 	alignment=ft.alignment.center,
				# 	border_radius=4,
				# 	border=ft.border.all(1, ft.Colors.BLACK45)
				# ),
				#
				# ft.Container(
				# 	content=ft.Text(value="Ausências",
				# 					size=12,
				# 					weight=ft.FontWeight.BOLD,
				# 					color=ft.Colors.BLACK),
				# 	bgcolor=ft.Colors.WHITE,
				# 	width=120,
				# 	alignment=ft.alignment.center,
				# 	border_radius=4,
				# 	border=ft.border.all(1, ft.Colors.BLACK45)
				# ),

				ft.Container(
					content=ft.Text(value="Permuta",
									size=12,
									weight=ft.FontWeight.BOLD,
									color=ft.Colors.BLACK),
					bgcolor=ft.Colors.GREY_400,
					width=120,
					alignment=ft.alignment.center,
					border_radius=4,
					border=ft.border.all(1, ft.Colors.BLACK45)
				),

				ft.Container(
					content=ft.Text(value="Compensação",
									size=12,
									weight=ft.FontWeight.BOLD,
									color=ft.Colors.BLACK),
					bgcolor=ft.Colors.BROWN_200,
					width=120,
					alignment=ft.alignment.center,
					border_radius=4,
					border=ft.border.all(1, ft.Colors.BLACK45)
				),

				ft.Container(
					content=ft.Text(value="TAC",
									size=12,
									weight=ft.FontWeight.BOLD,
									color=ft.Colors.WHITE),
					bgcolor=ft.Colors.BLACK,
					width=120,
					alignment=ft.alignment.center,
					border_radius=4,
					border=ft.border.all(1, ft.Colors.BLACK45)
				),

			],
			spacing=20,
			alignment=ft.MainAxisAlignment.CENTER,

		)

		return ft.Column(
			controls=[header,
					  row1,
					  legenda,
					  container_tabela_dinamica,
					  row2],
			horizontal_alignment=ft.CrossAxisAlignment.CENTER,
			spacing=15,
			expand=True
		)