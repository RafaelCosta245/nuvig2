import flet as ft
import os
import datetime
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from .base_screen import BaseScreen
from database.database_manager import DatabaseManager
from utils.google_drive_utils import authenticate_google_drive, get_or_create_folder, upload_file_to_drive


# ---- Função de alerta ----
def show_alert_dialog(page, mensagem, success=True, on_close=None):
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Sucesso" if success else "Erro", color=ft.Colors.GREEN if success else ft.Colors.RED),
        content=ft.Text(mensagem),
        actions=[
            ft.TextButton(
                "OK",
                on_click=lambda e: (page.close(dlg), on_close(e) if callable(on_close) else None),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    # Se clicar fora do diálogo, também dispara o on_close
    dlg.on_dismiss = lambda e: (on_close(e) if callable(on_close) else None)
    page.open(dlg)


# ---- Função principal de backup ----
def backup_sqlite_para_drive(db_path, parent_folder_id=None):
    drive = authenticate_google_drive()

    # Buscar ou criar a pasta "NUVIG Backup"
    nuvig_backup_id = get_or_create_folder(drive, "NUVIG Backup", parent_folder_id)

    # Nome da subpasta com data e hora
    pasta_nome = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pasta_id = get_or_create_folder(drive, pasta_nome, nuvig_backup_id)

    # Envia o arquivo .db
    upload_file_to_drive(drive, db_path, pasta_id)


class BancoDadosScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "banco_dados"
        # Consultar o caminho salvo na inicialização
        self.db_manager = DatabaseManager()
        self.current_save_path = self.db_manager.get_root_path("save_path") or ""

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
                # Ativa loader
                set_loading(True, page)
                # Caminho do arquivo de banco de dados
                db_path = os.path.join("assets", "db", "nuvig.db")
                
                # Verificar se o arquivo existe
                if not os.path.exists(db_path):
                    if page:
                        # Desativa loader antes de exibir alerta
                        set_loading(False, page)
                        show_alert_dialog(page, "Arquivo nuvig.db não encontrado na pasta assets/db/", success=False)
                    return
                
                # Fazer backup para o Google Drive
                backup_sqlite_para_drive(db_path)
                
                # Mostrar alerta de sucesso e recarregar a página ao fechar o diálogo
                if page:
                    def _reload(_):
                        try:
                            # Recarrega a tela atual
                            self.navigate_to("banco_dados")
                        except Exception as ex:
                            print(f"[UI] Erro ao recarregar após backup: {ex}")
                    # Desativa loader antes de mostrar o diálogo
                    set_loading(False, page)
                    show_alert_dialog(page, "Banco de dados salvo com sucesso no Google Drive!", success=True, on_close=_reload)
                
            except Exception as error:
                # Mostrar alerta de erro
                page = getattr(e, "page", None) or self.page
                if page:
                    # Garante desligar loader em erro
                    try:
                        set_loading(False, page)
                    except Exception:
                        pass
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

        # Container de carregamento (loader)
        load_container = ft.Container(width=50, height=50, alignment=ft.alignment.center)

        def set_loading(is_loading, page_ref=None):
            try:
                load_container.content = ft.ProgressRing() if is_loading else None
                # Atualiza apenas se já estiver em página (ex.: em cliques)
                if page_ref is not None:
                    load_container.update()
            except AssertionError as assert_ex:
                # Caso chamado antes de estar na página
                print(f"[UI][LOADER] Update precoce ignorado: {assert_ex}")

        def change_path(e):
            """Função para alterar o caminho de salvamento dos PDFs"""
            try:
                # Obter a página do evento
                page = getattr(e, "page", None)
                if page is None and hasattr(e, "control") and hasattr(e.control, "page"):
                    page = e.control.page
                if page is None:
                    page = self.page

                if not page:
                    print("[Change Path] Erro: Não foi possível obter referência da página")
                    return

                # Criar file picker para selecionar pasta
                def folder_picker_result(e):
                    try:
                        # Oculta loader ao finalizar callback
                        set_loading(False, page)
                        if e.path and os.path.isdir(e.path):
                            # Atualizar no banco de dados
                            success = self.db_manager.set_root_path("save_path", e.path)

                            if success:
                                # Mostrar alerta de sucesso
                                show_alert_dialog(
                                    page,
                                    f"Caminho atualizado com sucesso!\n\nNovo caminho: {e.path}",
                                    success=True
                                )

                                # Atualizar o valor local
                                self.current_save_path = e.path
                                saved_path.value = e.path
                                saved_path.update()

                                print(f"[Change Path] Caminho atualizado para: {e.path}")
                            else:
                                show_alert_dialog(
                                    page,
                                    "Erro ao salvar o novo caminho no banco de dados.",
                                    success=False
                                )
                        else:
                            show_alert_dialog(
                                page,
                                "Caminho inválido selecionado.",
                                success=False
                            )
                    except Exception as ex:
                        print(f"[Change Path] Erro ao processar seleção: {ex}")
                        show_alert_dialog(
                            page,
                            f"Erro ao processar a seleção: {str(ex)}",
                            success=False
                        )

                # Criar e configurar o file picker
                picker = ft.FilePicker(on_result=folder_picker_result)
                picker_dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("Selecionar Pasta de Salvamento", weight=ft.FontWeight.BOLD),
                    content=ft.Text("Escolha a pasta onde os arquivos PDF serão salvos:"),
                    actions=[
                        ft.TextButton("Selecionar Pasta", on_click=lambda e: picker.get_directory_path()),
                        ft.TextButton("Cancelar", on_click=lambda e: page.close(picker_dialog))
                    ],
                    actions_alignment=ft.MainAxisAlignment.END
                )

                # Adicionar o picker ao overlay da página se ainda não estiver
                if picker not in page.overlay:
                    page.overlay.append(picker)

                # Abrir o dialog
                set_loading(True, page)
                page.open(picker_dialog)

            except Exception as ex:
                print(f"[Change Path] Erro: {ex}")
                page = getattr(e, "page", None) or self.page
                if page:
                    show_alert_dialog(
                        page,
                        f"Erro ao alterar caminho: {str(ex)}",
                        success=False
                    )


        def logout_status(e=None):
            """Verifica status de login do Gmail e realiza login/logout conforme contexto.

            Comportamento:
            - Ao carregar a tela (chamada sem clique), verifica a coluna roots.credentials:
              - Se vazio/nulo: ajusta UI para 'desconectado'.
              - Se houver conteúdo: tenta autenticar e, se ok, ajusta UI para 'conectado'.
            - Ao clicar no botão:
              - Se estiver conectado: faz logout (limpa roots.credentials) e ajusta UI para 'desconectado'.
              - Se estiver desconectado: faz login (authenticate_google_drive) e ajusta UI para 'conectado'.
            """
            # Resolve page
            page = getattr(e, "page", None)
            if page is None and hasattr(e, "control") and hasattr(e.control, "page"):
                page = e.control.page
            if page is None:
                page = self.page

            # Lê valor cru da coluna path (roots.name='credentials')
            try:
                rows = self.db_manager.execute_query("SELECT path FROM roots WHERE name = ?", ("credentials",))
                raw_path = None
                if rows and rows[0]:
                    raw_path = rows[0][0]
                print(f"[UI][AUTH] Valor atual em roots.credentials: {('vazio' if not raw_path else 'preenchido')}\n")
            except Exception as ex:
                print(f"[UI][AUTH] Erro ao consultar roots.credentials: {ex}")
                raw_path = None

            # Determina estado atual
            is_connected = bool(raw_path and str(raw_path).strip() not in ("", "null", "None"))

            # Se veio de clique no botão, alterna o estado
            if e is not None and hasattr(e, "control"):
                # Mostra loader durante a operação
                set_loading(True, page)
                if is_connected:
                    # Logout: limpa credenciais no banco
                    try:
                        self.db_manager.execute_command("UPDATE roots SET path = NULL WHERE name = ?", ("credentials",))
                        self.db_manager.connection.commit()
                        print("[UI][AUTH] Logout realizado. Credenciais limpas no banco.")
                        is_connected = False
                        # Notifica o MainApp sobre o logout
                        if hasattr(self, 'app') and hasattr(self.app, 'logout'):
                            self.app.logout()
                    except Exception as ex:
                        print(f"[UI][AUTH] Erro ao realizar logout: {ex}")
                else:
                    # Login: autentica e salva via utilitário central
                    try:
                        from utils.google_drive_utils import authenticate_google_drive
                        authenticate_google_drive()
                        print("[UI][AUTH] Login concluído e credenciais salvas no banco (via utilitário).")
                        is_connected = True
                        # Notifica o MainApp sobre login bem-sucedido
                        if hasattr(self, 'app') and hasattr(self.app, 'set_authenticated'):
                            self.app.set_authenticated(True)
                    except Exception as ex:
                        print(f"[UI][AUTH] Erro ao realizar login: {ex}")
                        is_connected = False
                # Oculta loader ao final do clique
                set_loading(False, page)

            # Atualiza UI conforme estado
            if not is_connected:
                text_login.content.value = "Gmail desconectado ❌"
                btn_logout.text = "Login Gmail"
                btn_logout.icon = ft.Icons.LOGIN
            else:
                # Quando conectado, garantir autenticação vigente em carregamento inicial
                if e is None:
                    try:
                        from utils.google_drive_utils import authenticate_google_drive
                        authenticate_google_drive()
                    except Exception as ex:
                        print(f"[UI][AUTH] Erro ao validar sessão no carregamento: {ex}")
                text_login.content.value = "Gmail conectado ✅"
                btn_logout.text = "Logout Gmail"
                btn_logout.icon = ft.Icons.LOGOUT

            # Refresca elementos somente se os controles já estiverem na página (evento de clique)
            if e is not None:
                try:
                    text_login.content.update()
                    text_login.update()
                    btn_logout.update()
                    load_container.update()
                except AssertionError as assert_ex:
                    print(f"[UI][AUTH] Ignorando update precoce: {assert_ex}")


        text_path = ft.Container(
                    content=ft.Text(value="Pasta de relatórios:",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLACK,
                                    text_align=ft.TextAlign.CENTER),
                    # bgcolor=ft.Colors.LIGHT_GREEN,
                    width=250,
                    alignment=ft.alignment.center,
                    border_radius=4,
                    # border=ft.border.all(1, ft.Colors.BLACK45)
                )

        text_login = ft.Container(
            content=ft.Text(value="Gmail desconectado ❌",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                            text_align=ft.TextAlign.CENTER),
            # bgcolor=ft.Colors.LIGHT_GREEN,
            width=250,
            alignment=ft.alignment.center,
            border_radius=4,
            # border=ft.border.all(1, ft.Colors.BLACK45)
        )

        saved_path = ft.TextField(
            width=600,
            bgcolor=ft.Colors.WHITE,
            disabled=True,
            value=self.current_save_path  # Definir valor inicial consultado do banco
        )

        btn_change_path =ft.ElevatedButton(
                                    text="Alterar Pasta",
                                    icon=ft.Icons.CHANGE_CIRCLE,
                                    color=ft.Colors.BLACK,
                                    bgcolor=ft.Colors.WHITE,
                                    style=ft.ButtonStyle(
                                        shape=ft.RoundedRectangleBorder(radius=4),
                                        side=ft.BorderSide(
                                            width=1,
                                            color=ft.Colors.BLACK
                                        )
                                    ),
                                    tooltip="Escolhe um novo diretório para salvar os arquivos",
                                    width=150,
                                    height=30,
                                    on_click=change_path
                                )

        # Botão de login/logout já definido abaixo como btn_logout

        btn_logout = ft.ElevatedButton(
            text="Logout Gmail",
            #icon=ft.Icons.LOGOUT,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=4),
                side=ft.BorderSide(
                    width=1,
                    color=ft.Colors.BLACK
                )
            ),
            tooltip="Faz logout no usuário de Gmail registrado",
            width=150,
            height=30,
            on_click=logout_status
        )

        # Executa verificação inicial de status de login
        logout_status(None)

        return ft.Column([
            header,
            ft.Row([
                card_backup_db(),
                card_import_db(),
            ],
                spacing=20, alignment=ft.MainAxisAlignment.CENTER),
            load_container,
            text_path,
            saved_path,
            btn_change_path,
            ft.Container(height=20),
            text_login,
            btn_logout

        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
