import flet as ft
import os
import shutil
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from .base_screen import BaseScreen
from utils.google_drive_utils import authenticate_google_drive, get_or_create_folder


class ImportDBScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "import_db"

	def get_content(self) -> ft.Control:
		# Variável para manter referência à página atual durante o fluxo do FilePicker
		current_page = None
		cloud_list = ft.ListView(spacing=8, padding=10, height=300, width=500)

		# Loader container para indicar processamento
		load_container = ft.Container(width=50, height=50, alignment=ft.alignment.center)

		def set_loading(is_loading: bool, page_ref: ft.Page | None = None):
			try:
				load_container.content = ft.ProgressRing() if is_loading else None
				if page_ref is not None:
					load_container.update()
			except AssertionError as assert_ex:
				print(f"[ImportDB][LOADER] Update precoce ignorado: {assert_ex}")

		# Helper: alerta simples (sucesso/erro)
		def show_alert_dialog(page: ft.Page, mensagem: str, success: bool = True):
			dlg = ft.AlertDialog(
				modal=True,
				title=ft.Text("Sucesso" if success else "Erro",
							 color=ft.Colors.GREEN if success else ft.Colors.RED),
				content=ft.Text(mensagem),
				actions=[ft.TextButton("OK", on_click=lambda e: page.close(dlg))],
				actions_alignment=ft.MainAxisAlignment.END,
			)
			page.open(dlg)

		# ---- Autenticação com reutilização de credenciais ----
		def autenticar_drive():
			return authenticate_google_drive()

		# ---- Buscar pasta no Google Drive ----
		def get_folder_id(drive, nome_pasta, parent_id=None):
			query = f"title='{nome_pasta}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
			if parent_id:
				query += f" and '{parent_id}' in parents"
			folder_list = drive.ListFile({'q': query}).GetList()
			if folder_list:
				return folder_list[0]['id']
			return None

		# ---- Listar subpastas com nuvig.db ----
		def list_backup_subfolders(drive, nuvig_backup_id):
			query = f"'{nuvig_backup_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
			subfolders = drive.ListFile({'q': query}).GetList()
			items = []
			for folder in subfolders:
				folder_id = folder['id']
				folder_name = folder['title']
				file_query = f"'{folder_id}' in parents and title='nuvig.db' and trashed=false"
				files = drive.ListFile({'q': file_query}).GetList()
				if files:
					items.append({
						"folder_id": folder_id,
						"folder_name": folder_name,
						"file_id": files[0]['id'],
					})
			# Ordena por nome desc (timestamp YYYY-MM-DD_HH-MM-SS)
			items.sort(key=lambda x: x["folder_name"], reverse=True)
			return items

		# Helper: confirmação (sim/não)
		def show_confirm_dialog(page: ft.Page, titulo: str, mensagem: str, on_yes, on_no=None):
			dlg: ft.AlertDialog
			def _yes(e):
				page.close(dlg)
				if callable(on_yes):
					on_yes()
			def _no(e):
				page.close(dlg)
				if callable(on_no):
					on_no()
			dlg = ft.AlertDialog(
				modal=True,
				title=ft.Text(titulo),
				content=ft.Text(mensagem),
				actions=[
					ft.TextButton("Não", on_click=_no),
					ft.TextButton("Sim", on_click=_yes),
				],
				actions_alignment=ft.MainAxisAlignment.END,
			)
			page.open(dlg)

		def populate_cloud_list(page: ft.Page):
			try:
				drive = autenticar_drive()
				nuvig_backup_id = get_folder_id(drive, "NUVIG Backup", None)
				cloud_list.controls.clear()
				if not nuvig_backup_id:
					cloud_list.controls.append(ft.Text("Pasta 'NUVIG Backup' não encontrada no Drive."))
					page.update()
					# Esconde loader somente após lista ser atualizada na tela
					set_loading(False, page)
					return
				entries = list_backup_subfolders(drive, nuvig_backup_id)
				if not entries:
					cloud_list.controls.append(ft.Text("Nenhuma versão de backup encontrada."))
					page.update()
					# Esconde loader após atualizar lista vazia
					set_loading(False, page)
					return
				def make_on_tap(entry):
					def _handler(e):
						# Mostra loader durante o download do arquivo selecionado
						set_loading(True, page)
						def do_import():
							try:
								dest_dir = os.path.join("assets", "db")
								os.makedirs(dest_dir, exist_ok=True)
								dest_path = os.path.join(dest_dir, "nuvig.db")
								file = drive.CreateFile({'id': entry['file_id']})
								file.GetContentFile(dest_path)
								show_alert_dialog(page, "Banco de dados importado com sucesso da nuvem!", success=True)
							except Exception as ex:
								show_alert_dialog(page, f"Falha ao importar da nuvem: {ex}", success=False)
							finally:
								# Esconde loader após concluir o download
								set_loading(False, page)
						show_confirm_dialog(
							page,
							"Importar banco de dados?",
							f"Você deseja importar o banco da pasta '{entry['folder_name']}'? Isso irá sobrescrever o arquivo local.",
							on_yes=do_import,
						)
					return _handler
				for entry in entries:
					cloud_list.controls.append(
						ft.ListTile(
							title=ft.Text(entry["folder_name"]),
							leading=ft.Icon(ft.Icons.FOLDER),
							trailing=ft.Icon(ft.Icons.DOWNLOAD),
							on_click=make_on_tap(entry)
						)
					)
				page.update()
				# Esconde loader somente após itens adicionados e UI atualizada
				set_loading(False, page)
			except Exception as ex:
				show_alert_dialog(page, f"Erro ao buscar backups na nuvem: {ex}", success=False)

		def import_cloud(e):
			# Resolve a page e popula a lista de backups disponíveis
			nonlocal current_page
			page = getattr(e, "page", None)
			if page is None and hasattr(e, "control") and hasattr(e.control, "page"):
				page = e.control.page
			if page is None:
				page = self.page
			else:
				self.page = page
			current_page = page
			if page is None:
				return
			# Liga loader durante a busca na nuvem
			set_loading(True, page)
			try:
				populate_cloud_list(page)
			except Exception as ex:
				print(f"[ImportDB] Erro ao popular lista da nuvem: {ex}")
				set_loading(False, page)

		header = ft.Container(
			content=ft.Text(
				"Importar Banco de Dados",
				size=28,
				color=ft.Colors.BLACK,
				weight=ft.FontWeight.BOLD,
				text_align=ft.TextAlign.CENTER
			),
			padding=ft.padding.only(bottom=20),
			alignment=ft.alignment.center
		)

		# FilePicker e callback de resultado
		def on_file_picked(result: ft.FilePickerResultEvent):
			nonlocal current_page
			page = current_page
			if page is None:
				return
			if result is None or not result.files:
				return
			selected = result.files[0]
			src_path = getattr(selected, "path", None)
			if not src_path or not os.path.isfile(src_path):
				show_alert_dialog(page, "Arquivo inválido selecionado.", success=False)
				return
			if not src_path.lower().endswith(".db"):
				show_alert_dialog(page, "Selecione um arquivo com extensão .db.", success=False)
				return

			dest_dir = os.path.join("assets", "db")
			dest_path = os.path.join(dest_dir, "nuvig.db")
			os.makedirs(dest_dir, exist_ok=True)

			def do_copy():
				try:
					shutil.copy2(src_path, dest_path)
					show_alert_dialog(page, "Banco de dados importado com sucesso!", success=True)
				except Exception as ex:
					show_alert_dialog(page, f"Falha ao substituir o banco de dados: {ex}", success=False)

			if os.path.exists(dest_path):
				show_confirm_dialog(
					page,
					"Sobrescrever arquivo?",
					"Já existe um arquivo 'nuvig.db' na pasta. Deseja sobrescrever?",
					on_yes=do_copy,
					on_no=lambda: None,
				)
			else:
				do_copy()

		file_picker = ft.FilePicker(on_result=on_file_picked)

		def import_local(e):
			nonlocal current_page
			# Resolve a page a partir do evento
			page = getattr(e, "page", None)
			if page is None and hasattr(e, "control") and hasattr(e.control, "page"):
				page = e.control.page
			if page is None:
				page = self.page
			else:
				self.page = page
			current_page = page
			if page is None:
				return
			# Adiciona o FilePicker ao overlay se ainda não estiver
			if file_picker not in page.overlay:
				page.overlay.append(file_picker)
				page.update()
			# Abre seletor permitindo apenas .db
			file_picker.pick_files(allow_multiple=False, allowed_extensions=["db"], dialog_title="Selecione um arquivo .db")


		def import_cloud(e):
			# Resolve a page e popula a lista de backups disponíveis
			nonlocal current_page
			page = getattr(e, "page", None)
			if page is None and hasattr(e, "control") and hasattr(e.control, "page"):
				page = e.control.page
			if page is None:
				page = self.page
			else:
				self.page = page
			current_page = page
			if page is None:
				return
			# Liga loader durante a busca na nuvem
			set_loading(True, page)
			try:
				populate_cloud_list(page)
			except Exception as ex:
				print(f"[ImportDB] Erro ao popular lista da nuvem: {ex}")

		card_local = ft.Card(
			content=ft.Container(
				content=ft.Column(
					[
						ft.Icon(ft.Icons.UPLOAD_FILE, size=40, color="blue"),
						ft.Text("Importar do Computador", size=14, weight="bold"),
						ft.Text("Selecione um arquivo .db do seu dispositivo."),
						ft.ElevatedButton(text="Escolher Arquivo",
										  icon=ft.Icons.FOLDER_OPEN,
										  color=ft.Colors.BLACK,
										  on_click=import_local),
					],
					horizontal_alignment="center",
					spacing=10,
				),
				border=ft.border.all(1, ft.Colors.GREY),
				bgcolor=ft.Colors.WHITE,
				border_radius=12,
				padding=20,
				width=400,

			),
		)

		load_container = ft.Container(width=50, height=50, alignment=ft.alignment.center)

		card_nuvem = ft.Card(
			content=ft.Container(
				content=ft.Column(
					[
						ft.Icon(ft.Icons.CLOUD, size=40, color="green"),
						ft.Text("Importar da Nuvem", size=14, weight="bold"),
						ft.Text("Busque um arquivo salvo no Google Drive."),
						ft.ElevatedButton(text="Procurar na Nuvem",
										  icon=ft.Icons.CLOUD_DOWNLOAD,
										  color=ft.Colors.BLACK,
										  on_click=import_cloud),
					],
					horizontal_alignment="center",
					spacing=10,
				),
				border=ft.border.all(1, ft.Colors.GREY),
				bgcolor=ft.Colors.WHITE,
				border_radius=12,
				padding=20,
				width=400,
			),
		)

		list_container = ft.Container(
							width=400,
							height=250,
							content=cloud_list,
							border=ft.border.all(1, ft.Colors.GREY),
							bgcolor=ft.Colors.WHITE,
							border_radius=11,
		)

		return ft.Column([
			header,
			ft.Row([
				card_local,
				card_nuvem,
			], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
			ft.Container(height=10),
			load_container,
			ft.Text("Backups encontrados na nuvem:", weight=ft.FontWeight.BOLD),
			list_container,
		], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
