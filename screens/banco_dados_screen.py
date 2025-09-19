import flet as ft
import os
import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from .base_screen import BaseScreen


# ---- Função de alerta ----
def show_alert_dialog(page, mensagem, success=True):
	dlg = ft.AlertDialog(
		modal=True,
		title=ft.Text("Sucesso" if success else "Erro", color=ft.Colors.GREEN if success else ft.Colors.RED),
		content=ft.Text(mensagem),
		actions=[
			ft.TextButton("OK", on_click=lambda e: page.close(dlg)),
		],
		actions_alignment=ft.MainAxisAlignment.END,
	)
	page.open(dlg)


# ---- Autenticação com reutilização de credenciais ----
def autenticar_drive():
	gauth = GoogleAuth()

	# Caminho para o arquivo client_secrets.json
	caminho_client = os.path.join("assets", "json", "client_secrets.json")

	# Caminho para salvar/reutilizar credenciais
	caminho_credentials = os.path.join("assets", "json", "credentials.json")

	# Verifica se o arquivo client_secrets.json existe
	if not os.path.exists(caminho_client):
		raise FileNotFoundError(
			f"Arquivo client_secrets.json não encontrado em: {caminho_client}. "
			"Certifique-se de que o arquivo está no diretório 'assets/json/'."
		)

	# Configura o caminho do client_secrets.json
	gauth.LoadClientConfigFile(caminho_client)

	# Tenta carregar credenciais salvas
	if os.path.exists(caminho_credentials):
		try:
			gauth.LoadCredentialsFile(caminho_credentials)
			if gauth.credentials is None or gauth.credentials.invalid:
				print("Credenciais salvas inválidas, iniciando nova autenticação...")
				gauth.LocalWebserverAuth()
				gauth.SaveCredentialsFile(caminho_credentials)
			else:
				print("Usando credenciais salvas.")
		except Exception as e:
			print(f"Erro ao carregar credenciais salvas: {str(e)}. Iniciando nova autenticação...")
			gauth.LocalWebserverAuth()
			gauth.SaveCredentialsFile(caminho_credentials)
	else:
		# Primeira autenticação: abre o navegador
		print("Nenhuma credencial salva encontrada. Autenticando via navegador...")
		gauth.LocalWebserverAuth()
		gauth.SaveCredentialsFile(caminho_credentials)

	return GoogleDrive(gauth)


# ---- Buscar ou criar pasta no Google Drive ----
def get_or_create_folder(drive, nome_pasta, parent_id=None):
	# Buscar pasta existente pelo nome
	query = f"title='{nome_pasta}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
	if parent_id:
		query += f" and '{parent_id}' in parents"

	try:
		folder_list = drive.ListFile({'q': query}).GetList()
	except Exception as e:
		raise Exception(f"Erro ao buscar pasta '{nome_pasta}': {str(e)}")

	# Se a pasta já existe, retorna seu ID
	if folder_list:
		return folder_list[0]['id']

	# Se não existe, cria a pasta
	pasta = drive.CreateFile({
		"title": nome_pasta,
		"mimeType": "application/vnd.google-apps.folder",
		"parents": [{"id": parent_id}] if parent_id else []
	})
	pasta.Upload()
	return pasta["id"]


# ---- Fazer upload do arquivo para a pasta ----
def upload_arquivo(drive, file_path, folder_id):
	if not os.path.exists(file_path):
		raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

	arquivo = drive.CreateFile({
		"title": os.path.basename(file_path),
		"parents": [{"id": folder_id}]
	})
	arquivo.SetContentFile(file_path)
	arquivo.Upload()
	print(f"✔ Arquivo {file_path} enviado para a pasta ID={folder_id}")


# ---- Função principal de backup ----
def backup_sqlite_para_drive(db_path, parent_folder_id=None):
	drive = autenticar_drive()

	# Buscar ou criar a pasta "NUVIG Backup"
	nuvig_backup_id = get_or_create_folder(drive, "NUVIG Backup", parent_folder_id)

	# Nome da subpasta com data e hora
	pasta_nome = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
	pasta_id = get_or_create_folder(drive, pasta_nome, nuvig_backup_id)

	# Envia o arquivo .db
	upload_arquivo(drive, db_path, pasta_id)


class BancoDadosScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "banco_dados"

	def get_content(self) -> ft.Control:
		header = ft.Container(
			content=ft.Text(
				"Banco de dados",
				size=28,
				color=ft.Colors.BLACK,
				weight=ft.FontWeight.BOLD,
				text_align=ft.TextAlign.CENTER
			),
			padding=ft.padding.only(bottom=20),
			alignment=ft.alignment.center
		)

		def salvar_db(e):
			try:
				# Determina a página ativa a partir do evento; se não houver, tenta usar self.page
				# Tenta obter a página do evento, do controle, ou da instância
				page = getattr(e, "page", None)
				if page is None and hasattr(e, "control") and hasattr(e.control, "page"):
					page = e.control.page
				if page is None:
					page = self.page
				else:
					# Persiste a referência da página para usos futuros
					self.page = page
				# Caminho do arquivo de banco de dados
				db_path = os.path.join("assets", "db", "nuvig.db")
				
				# Verificar se o arquivo existe
				if not os.path.exists(db_path):
					if page:
						show_alert_dialog(page, "Arquivo nuvig.db não encontrado na pasta assets/db/", success=False)
					return
				
				# Fazer backup para o Google Drive
				backup_sqlite_para_drive(db_path)
				
				# Mostrar alerta de sucesso
				if page:
					show_alert_dialog(page, "Banco de dados salvo com sucesso no Google Drive!", success=True)
				
			except Exception as error:
				# Mostrar alerta de erro
				page = getattr(e, "page", None) or self.page
				if page:
					show_alert_dialog(page, f"Erro ao salvar banco de dados: {str(error)}", success=False)


		def card_backup_db() -> ft.Control:
			return ft.Container(
				content=ft.Column(
					controls=[
						ft.Text("☁️ Backup do Banco de dados", size=18, weight=ft.FontWeight.BOLD,
								text_align=ft.TextAlign.CENTER),
						ft.Text("Salvar BD na nuvem", size=12, color=ft.Colors.GREY,
								text_align=ft.TextAlign.CENTER),
						ft.Container(height=15),
						ft.TextButton(
							text="Salvar",
							icon=ft.Icons.SAVE,
							on_click=lambda e: salvar_db(e),
						),
					],
					horizontal_alignment=ft.CrossAxisAlignment.START,
					spacing=5,
				),
				padding=ft.padding.all(8),
				border=ft.border.all(1, ft.Colors.GREY),
				border_radius=12,
				bgcolor=ft.Colors.WHITE,
				width=310,
				height=140
			)

		def card_import_db() -> ft.Control:
			return ft.Container(
				content=ft.Column(
					controls=[
						ft.Text("📥 Importar Banco de Dados", size=18, weight=ft.FontWeight.BOLD,
								text_align=ft.TextAlign.CENTER),
						ft.Text("Importar arquivo da Nuvem", size=12, color=ft.Colors.GREY,
								text_align=ft.TextAlign.CENTER),
						ft.Container(height=15),
						ft.TextButton(
							text="Abrir",
							icon=ft.Icons.ARROW_FORWARD,
							on_click=lambda e: self.navigate_to("import_db"),
						),
					],
					horizontal_alignment=ft.CrossAxisAlignment.START,
					spacing=5,
				),
				padding=ft.padding.all(8),
				border=ft.border.all(1, ft.Colors.GREY),
				border_radius=12,
				bgcolor=ft.Colors.WHITE,
				width=300,
				height=140
			)

		return ft.Column([
			header,
			ft.Row([
				card_backup_db(),
				card_import_db(),
			], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
		], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
