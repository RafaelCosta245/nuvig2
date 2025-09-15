import os
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


# ---- Buscar pasta no Google Drive ----
def get_folder_id(drive, nome_pasta, parent_id=None):
	# Buscar pasta existente pelo nome
	query = f"title='{nome_pasta}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
	if parent_id:
		query += f" and '{parent_id}' in parents"

	try:
		folder_list = drive.ListFile({'q': query}).GetList()
	except Exception as e:
		raise Exception(f"Erro ao buscar pasta '{nome_pasta}': {str(e)}")

	# Se a pasta existe, retorna seu ID
	if folder_list:
		return folder_list[0]['id']

	# Se não existe, retorna None ou levanta erro
	return None


# ---- Listar subpastas e verificar arquivos ----
def list_backup_versions(drive, nuvig_backup_id):
	# Query para listar subpastas dentro de "NUVIG Backup"
	query = f"'{nuvig_backup_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
	subfolders = drive.ListFile({'q': query}).GetList()

	versions = []

	for folder in subfolders:
		folder_id = folder['id']
		folder_name = folder['title']  # Nome da subpasta (timestamp)

		# Query para verificar se há um arquivo "nuvig.db" na subpasta
		file_query = f"'{folder_id}' in parents and title='nuvig.db' and trashed=false"
		files = drive.ListFile({'q': file_query}).GetList()

		if files:
			versions.append(folder_name)

	return versions


# ---- Função principal para listar versões ----
def listar_versoes_backup(parent_folder_id=None):
	drive = autenticar_drive()

	# Buscar a pasta "NUVIG Backup"
	nuvig_backup_id = get_folder_id(drive, "NUVIG Backup", parent_folder_id)

	if not nuvig_backup_id:
		print("Pasta 'NUVIG Backup' não encontrada.")
		return

	# Listar as versões (subpastas com nuvig.db)
	versions = list_backup_versions(drive, nuvig_backup_id)

	if not versions:
		print("Nenhuma versão de backup encontrada.")
	else:
		print("Versões de backup disponíveis (datas e horas):")
		for version in sorted(versions):  # Ordena por timestamp
			print(f"- {version}")


# ---- Executar exemplo ----
if __name__ == "__main__":
	parent_folder = None
	try:
		listar_versoes_backup(parent_folder)
	except Exception as e:
		print(f"Erro ao listar backups: {str(e)}")