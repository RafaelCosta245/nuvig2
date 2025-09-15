import os
import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


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


# ---- Executar exemplo ----
if __name__ == "__main__":
	db_file = "assets/db/nuvig.db"
	parent_folder = None
	try:
		backup_sqlite_para_drive(db_file, parent_folder)
	except Exception as e:
		print(f"Erro ao executar o backup: {str(e)}")