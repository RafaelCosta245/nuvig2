import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from database.database_manager import DatabaseManager
import tempfile
import json
from oauth2client.client import OAuth2Credentials


def authenticate_google_drive():
    """
    Função centralizada para autenticação do Google Drive
    Consulta credenciais do banco de dados e faz nova autenticação se necessário

    Returns:
        GoogleDrive: Instância autenticada do Google Drive
    """
    db_manager = DatabaseManager()

    print("[GD][AUTH] Iniciando autenticação do Google Drive...")
    print("[GD][AUTH] Lendo client_secrets e credentials do banco (tabela roots)...")
    # Tenta obter credenciais do banco
    client_secrets = db_manager.get_google_credentials('client_secrets')
    credentials = db_manager.get_google_credentials('credentials')
    print(f"[GD][AUTH] client_secrets obtido? {'SIM' if bool(client_secrets) else 'NÃO'}")
    print(f"[GD][AUTH] credentials obtido? {'SIM' if bool(credentials) else 'NÃO'}")

    # Se não tem client_secrets no banco, aborta com instrução clara
    if not client_secrets:
        raise RuntimeError(
            "Client secrets não encontrados no banco (roots.name='client_secrets'). "
            "Cadastre o JSON de client_secrets na tabela roots para proceder."
        )

    # Escreve client_secrets num arquivo temporário e usa LoadClientConfigFile (API suportada)
    gauth = GoogleAuth()
    # Força obtenção de refresh_token e evita salvar em arquivo
    try:
        gauth.settings["get_refresh_token"] = True
        gauth.settings["save_credentials"] = False
        gauth.settings["oauth_scope"] = ["https://www.googleapis.com/auth/drive"]
        print("[GD][AUTH] Settings definidos: get_refresh_token=True, save_credentials=False")
    except Exception as _:
        pass
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp_cs:
        json.dump(client_secrets, tmp_cs)
        tmp_cs_path = tmp_cs.name
    try:
        gauth.LoadClientConfigFile(tmp_cs_path)
        print("[GD][AUTH] Client config carregado a partir do JSON do banco (via arquivo temporário).")
    finally:
        # Remove o arquivo temporário de client secrets
        try:
            os.unlink(tmp_cs_path)
        except Exception:
            pass

    # Se existir credentials no banco, constroi OAuth2Credentials diretamente (sem arquivos)
    if credentials:
        try:
            cred_json_str = json.dumps(credentials)
            gauth.credentials = OAuth2Credentials.from_json(cred_json_str)
            print("[GD][AUTH] Credenciais reconstruídas a partir do banco.")
            # Prints de diagnóstico das credenciais
            try:
                print(f"[GD][AUTH] Tem refresh_token? {'SIM' if bool(getattr(gauth.credentials, 'refresh_token', None)) else 'NÃO'}")
                print(f"[GD][AUTH] access_token_expired? {getattr(gauth.credentials, 'access_token_expired', None)}")
                print(f"[GD][AUTH] invalid? {getattr(gauth.credentials, 'invalid', None)}")
            except Exception:
                pass
        except Exception as e:
            print(f"[Google Drive] Erro ao reconstruir credenciais do banco: {e}")

    # Se temos credenciais, tentar atualizar/validar sem pedir login
    if getattr(gauth, 'credentials', None):
        try:
            # Se expiradas e há refresh_token, tenta refresh
            if getattr(gauth.credentials, 'access_token_expired', False):
                if getattr(gauth.credentials, 'refresh_token', None):
                    print("[GD][AUTH] Token expirado, tentando refresh...")
                    gauth.Refresh()
                    print("[GD][AUTH] Refresh concluído. invalid?", getattr(gauth.credentials, 'invalid', None))
                else:
                    # Sem refresh_token, será necessário autenticar novamente
                    print("[GD][AUTH] Token expirado e NÃO há refresh_token. Marcar como inválido para reautenticar.")
                    gauth.credentials.invalid = True
        except Exception as e:
            print(f"[GD][AUTH] Falha ao refresh do token: {e}")
            gauth.credentials.invalid = True

    # Se ainda não há credenciais válidas, inicia fluxo de autenticação no navegador
    if not getattr(gauth, 'credentials', None) or getattr(gauth.credentials, 'invalid', True):
        print("[GD][AUTH] Credenciais inválidas ou ausentes, iniciando nova autenticação via navegador...")
        # Solicita refresh_token garantindo consentimento offline
        # pydrive2 lê estas flags das settings; reforçamos prompt/consent se flow existir
        try:
            if hasattr(gauth, 'flow') and gauth.flow and hasattr(gauth.flow, 'params'):
                gauth.flow.params.update({'access_type': 'offline', 'prompt': 'consent'})
                print("[GD][AUTH] flow.params atualizado com access_type=offline, prompt=consent")
        except Exception as _:
            pass
        gauth.LocalWebserverAuth()
        print("[GD][AUTH] Autenticação via navegador concluída.")

    # Após autenticar, salvar/atualizar as credenciais no banco
    if getattr(gauth, 'credentials', None):
        try:
            cred_json_str = gauth.credentials.to_json()
            cred_dict = json.loads(cred_json_str)
            print("[GD][AUTH] JSON de credenciais a ser salvo no banco (chaves):", list(cred_dict.keys()))
            print("[GD][AUTH] Tem refresh_token no salvo?", bool(cred_dict.get('refresh_token')))
            ok = db_manager.set_google_credentials('credentials', cred_dict)
            print("[GD][AUTH] Resultado do salvamento no banco: ", "SUCESSO" if ok else "FALHA")
        except Exception as e:
            print(f"[GD][AUTH] Falha ao salvar credenciais no banco: {e}")

    return GoogleDrive(gauth)


def get_or_create_folder(drive, nome_pasta, parent_id=None):
    """
    Busca ou cria pasta no Google Drive

    Args:
        drive: Instância do GoogleDrive
        nome_pasta (str): Nome da pasta
        parent_id (str, optional): ID da pasta pai

    Returns:
        str: ID da pasta
    """
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


def upload_file_to_drive(drive, file_path, folder_id):
    """
    Faz upload de arquivo para o Google Drive

    Args:
        drive: Instância do GoogleDrive
        file_path (str): Caminho local do arquivo
        folder_id (str): ID da pasta destino

    Returns:
        bool: True se sucesso
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    arquivo = drive.CreateFile({
        "title": os.path.basename(file_path),
        "parents": [{"id": folder_id}]
    })
    arquivo.SetContentFile(file_path)
    arquivo.Upload()
    print(f"✔ Arquivo {file_path} enviado para a pasta ID={folder_id}")
    return True
