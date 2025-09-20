
import flet as ft
import uuid
import random

from .base_screen import BaseScreen
import datetime
from database.database_manager import DatabaseManager

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
			print(f'Exportar PDF')

		def salvar_escala(e):
			print(f'Escala salva')

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
			first_date=datetime.datetime(2020, 1, 1),
			last_date=datetime.datetime(2030, 12, 31),
		)

		# Tenta anexar o datepicker ao overlay ao montar a tela
		try:
			if self.page and datepicker not in self.page.overlay:
				self.page.overlay.append(datepicker)
		except Exception:
			pass

		weekday = ""
		equipe = ""

		# --- Helpers de data ---
		def ddmmyyyy_to_yyyymmdd(s: str) -> str:
			try:
				parts = s.split("/")
				if len(parts) == 3 and all(parts):
					return f"{parts[2]}-{parts[1]}-{parts[0]}"
				return ""
			except Exception:
				return ""

		def is_valid_ddmmyyyy(s: str) -> bool:
			if not s or len(s) != 10:
				return False
			try:
				datetime.datetime.strptime(s, "%d/%m/%Y")
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
						_date_obj = datetime.datetime.strptime(novo_valor, "%d/%m/%Y").date()
						weekday = pt_weekdays[_date_obj.weekday()]
					except Exception:
						weekday = ""
					equipe = equipe_result
					team_text.value = f"{weekday} - Equipe {equipe}"
					# Atualiza a tabela dinâmica
					try:
						refresh_tabela_para_data_atual()
					except Exception:
						pass
			e.control.page.update()

		data = ft.TextField(label="Data", width=btn_data.width, hint_text="dd/mm/aaaa", bgcolor=ft.Colors.WHITE)
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

		row1 = ft.Row(
			controls=[btn_data, data, cont_team_text],
			spacing=20,
			alignment=ft.MainAxisAlignment.CENTER
		)




		# Inicializa com a data de hoje e atualiza equipe/weekday (nome do dia)
		try:
			today = datetime.date.today()
			weekday = pt_weekdays[today.weekday()]
			data.value = today.strftime("%d/%m/%Y")
			query_date = today.strftime("%Y-%m-%d")
			equipe = db.get_equipe_by_data(query_date) or ""
			team_text.value = f"{weekday} - Equipe {equipe}"
		except Exception:
			pass

		btn_save = ft.ElevatedButton(
            text="Salvar",
            icon=ft.Icons.SAVE,
            width=150,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.BLACK),
            ),
            on_click=salvar_escala
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
            on_click=exportar_pdf
        )

		row2 = ft.Row(
			controls=[btn_save, btn_export],
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
				}
			except Exception:
				pass
			# Define cor baseada no tipo
			cores = {
				"padrao": ft.Colors.LIGHT_GREEN,      # Verde claro - adição padrão inicial
				"obll": ft.Colors.YELLOW,             # Amarelo - OBLL
				"ferias": ft.Colors.BLUE_GREY_300,    # Azul acinzentado - Férias
				"licencas": ft.Colors.ORANGE,         # Laranja - Licenças
				"ausencias": ft.Colors.WHITE,         # Branco - Ausências (não licenças)
				"compensacao": ft.Colors.BROWN_200,   # Marrom claro - Compensações
				"permuta": ft.Colors.GREY_400,        # Cinza - Permutas
				"extra_diurno": ft.Colors.BLUE_200,   # Azul - Extra Diurno
				"extra_noturno": ft.Colors.INDIGO_200, # Índigo - Extra Noturno
			}
			bgcolor = cores.get(tipo, ft.Colors.LIGHT_GREEN)
			
			return ft.Draggable(
				group="policiais",
				data=item_id,
				content=ft.Container(
					content=ft.Text(label, size=12, text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
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
				data_sel = datetime.datetime.strptime(data_ddmmyyyy, "%d/%m/%Y").date()
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
					inicio_date = datetime.datetime.strptime(inicio_str, "%Y-%m-%d").date()
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
				rows_extras = db.execute_query("SELECT policial_id FROM extras WHERE data_id = ? AND operacao = 'OBLL'", (data_id,))
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
						return datetime.datetime.strptime(str(s).strip()[:10], "%Y-%m-%d").date()
					except Exception:
						return None
				data_sel = parse_iso(data_iso)
				if not data_sel:
					return
				print(f"[Férias] Verificando férias para data {data_iso} ({data_sel})")
				# Constrói conjunto de ids em férias
				ferias_ids = set()
				# Consultar todos os registros de férias dos policiais que estão nas colunas de acesso
				# Coleta pids das colunas 1..3
				pids = []
				for key in ["col1", "col2", "col3"]:
					for it in col_items[key]:
						pid = id_map.get(getattr(it, "data", ""), {}).get("id")
						if pid:
							pids.append(pid)
				print("[Férias] PIDs nas colunas de acesso:", pids)
				# Para eficiência, consulta férias de todos pids de uma vez (IN)
				if not pids:
					return
				placeholders = ",".join(["?"] * len(pids))
				rows = db.execute_query(
					f"SELECT policial_id, inicio1, fim1, inicio2, fim2, inicio3, fim3 FROM ferias WHERE policial_id IN ({placeholders})",
					tuple(pids),
				)
				print(f"[Férias] Registros ferias por policial_id: {len(rows)}")
				# Fallback: se não houver registros por policia_id, tentar por matricula
				if not rows:
					# Buscar matriculas dos pids
					mrows = db.execute_query(
						f"SELECT id, matricula FROM policiais WHERE id IN ({placeholders})",
						tuple(pids),
					)
					matriculas = [r["matricula"] for r in mrows if "matricula" in r.keys() and r["matricula"]]
					print("[Férias] Tentando fallback por matrícula:", matriculas)
					if matriculas:
						ph2 = ",".join(["?"] * len(matriculas))
						# Algumas bases usam coluna 'matricula' em ferias
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
				for r in rows:
					pid = rg(r, "policial_id")
					if in_range(data_sel, rg(r, "inicio1"), rg(r, "fim1")) or \
					   in_range(data_sel, rg(r, "inicio2"), rg(r, "fim2")) or \
					   in_range(data_sel, rg(r, "inicio3"), rg(r, "fim3")):
						ferias_ids.add(pid)
						print(f"[Férias] Policial em férias na data {data_iso}: pid={pid}, ranges=", rg(r, "inicio1"), rg(r, "fim1"), rg(r, "inicio2"), rg(r, "fim2"), rg(r, "inicio3"), rg(r, "fim3"))
				# Move itens dos acessos para col5 (Férias)
				if ferias_ids:
					print("[Férias] Movendo para coluna Férias ids:", ferias_ids)
					for key in ["col1", "col2", "col3"]:
						rem = []
						for it in col_items[key]:
							pid = id_map.get(getattr(it, "data", ""), {}).get("id")
							if pid in ferias_ids:
								# cria novo draggable para a coluna férias baseado nos dados do id_map
								pinfo = id_map.get(getattr(it, "data", ""), {})
								print(f"[Férias] Removendo de {key} e adicionando em Férias:", pinfo)
								col_items["col5"].append(make_draggable_policial(pinfo, "ferias"))
								rem.append(it)
						# remove os marcados
						for it in rem:
							col_items[key].remove(it)
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
						return datetime.datetime.strptime(str(s).strip()[:10], "%Y-%m-%d").date()
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
				placeholders = ",".join(["?" ] * len(pids))
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
					if in_range(data_sel, r["inicio"] if "inicio" in r.keys() else None, r["fim"] if "fim" in r.keys() else None):
						# Verifica se é licença ou ausência pelo campo 'licenca'
						motivo = ""
						try:
							motivo = (r["licenca"] or "").lower()
						except Exception:
							motivo = (r.get("licenca", "") or "").lower()
						if "licença" in motivo or "licenca" in motivo:
							lic_ids.add(pid)
							print(f"[Licenças] Policial em licença na data {data_iso}: pid={pid}, motivo='{motivo}', periodo=", r.get("inicio") if hasattr(r, "get") else r["inicio"], r.get("fim") if hasattr(r, "get") else r["fim"])
						else:
							aus_ids.add(pid)
							print(f"[Ausências] Policial em ausência na data {data_iso}: pid={pid}, motivo='{motivo}', periodo=", r.get("inicio") if hasattr(r, "get") else r["inicio"], r.get("fim") if hasattr(r, "get") else r["fim"])
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
							if len(col_items["col1"]) < 4:
								col_items["col1"].append(make_draggable_policial(pol_data, "compensacao"))
							elif len(col_items["col3"]) < 2:
								col_items["col3"].append(make_draggable_policial(pol_data, "compensacao"))
							else:
								col_items["col2"].append(make_draggable_policial(pol_data, "compensacao"))
							print(f"[Compensações] Adicionado aos acessos: {pol_data.get('qra') or pol_data.get('nome')}")
				
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
								print(f"[Compensações] Removendo de {key}: {id_map.get(getattr(it, 'data', ''), {}).get('qra') or id_map.get(getattr(it, 'data', ''), {}).get('nome')}")
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
							col_items["col7"].append(make_draggable_policial(pol_data, "compensacao"))
							print(f"[Compensações] Adicionado às ausências: {pol_data.get('qra') or pol_data.get('nome')}")
				
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
						print(f"[Permutas] Removendo solicitante de {key}: {solicitante_data.get('qra') or solicitante_data.get('nome')}")
				for it in rem:
					col_items[key].remove(it)
			
			# Adicionar solicitante às ausências
			col_items["col7"].append(make_draggable_policial(solicitante_data, "permuta"))
			print(f"[Permutas] Solicitante adicionado às ausências: {solicitante_data.get('qra') or solicitante_data.get('nome')}")
			
			# Adicionar permutado aos acessos
			if len(col_items["col1"]) < 4:
				col_items["col1"].append(make_draggable_policial(permutado_data, "permuta"))
			elif len(col_items["col3"]) < 2:
				col_items["col3"].append(make_draggable_policial(permutado_data, "permuta"))
			else:
				col_items["col2"].append(make_draggable_policial(permutado_data, "permuta"))
			print(f"[Permutas] Permutado adicionado aos acessos: {permutado_data.get('qra') or permutado_data.get('nome')}")

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
						print(f"[Permutas] Removendo permutado de {key}: {permutado_data.get('qra') or permutado_data.get('nome')}")
				for it in rem:
					col_items[key].remove(it)
			
			# Adicionar permutado às ausências
			col_items["col7"].append(make_draggable_policial(permutado_data, "permuta"))
			print(f"[Permutas] Permutado adicionado às ausências: {permutado_data.get('qra') or permutado_data.get('nome')}")
			
			# Adicionar solicitante aos acessos
			if len(col_items["col1"]) < 4:
				col_items["col1"].append(make_draggable_policial(solicitante_data, "permuta"))
			elif len(col_items["col3"]) < 2:
				col_items["col3"].append(make_draggable_policial(solicitante_data, "permuta"))
			else:
				col_items["col2"].append(make_draggable_policial(solicitante_data, "permuta"))
			print(f"[Permutas] Solicitante adicionado aos acessos: {solicitante_data.get('qra') or solicitante_data.get('nome')}")

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
								print(f"[Extras] Extra (turno indefinido, assumindo diurno): {pol_data.get('qra') or pol_data.get('nome')}")
							
							# Distribuir entre acessos (similar à distribuição padrão)
							# Prioridade: col1 (até 4), col3 (até 2), col2 (restante)
							if len(col_items["col1"]) < 4:
								col_items["col1"].append(make_draggable_policial(pol_data, tipo))
							elif len(col_items["col3"]) < 2:
								col_items["col3"].append(make_draggable_policial(pol_data, tipo))
							else:
								col_items["col2"].append(make_draggable_policial(pol_data, tipo))
							
							print(f"[Extras] Adicionado aos acessos: {pol_data.get('qra') or pol_data.get('nome')} ({turno})")
				
				update_columns()
			except Exception as ex:
				print("[Extras] Erro ao aplicar extras:", ex)
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

		col1_drag = ft.DragTarget(group="policiais", content=col1, on_will_accept=drag_will_accept, on_accept=drag_accept, on_leave=drag_leave, data="col1")
		col2_drag = ft.DragTarget(group="policiais", content=col2, on_will_accept=drag_will_accept, on_accept=drag_accept, on_leave=drag_leave, data="col2")
		col3_drag = ft.DragTarget(group="policiais", content=col3, on_will_accept=drag_will_accept, on_accept=drag_accept, on_leave=drag_leave, data="col3")
		col4_drag = ft.DragTarget(group="policiais", content=col4, on_will_accept=drag_will_accept, on_accept=drag_accept, on_leave=drag_leave, data="col4")
		col5_drag = ft.DragTarget(group="policiais", content=col5, on_will_accept=drag_will_accept, on_accept=drag_accept, on_leave=drag_leave, data="col5")
		col6_drag = ft.DragTarget(group="policiais", content=col6, on_will_accept=drag_will_accept, on_accept=drag_accept, on_leave=drag_leave, data="col6")
		col7_drag = ft.DragTarget(group="policiais", content=col7, on_will_accept=drag_will_accept, on_accept=drag_accept, on_leave=drag_leave, data="col7")

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
		def refresh_tabela_para_data_atual():
			if not equipe or not data.value or len(data.value) != 10:
				return
			# Sempre começar limpando todas as colunas
			clear_all_columns()
			print("[Calendario] Refresh para data:", data.value, "equipe:", equipe)
			pols = buscar_policiais_elegiveis(equipe, data.value)
			print(f"[Calendario] Policiais elegíveis ({len(pols)}):", [p.get("qra") or p.get("nome") for p in pols])
			distribuir_policiais(pols)
			# Aplica compensações: adiciona aos acessos e ausências
			aplicar_compensacoes(data.value)
			# Aplica permutas: troca policiais entre acessos e ausências
			aplicar_permutas(data.value)
			# Aplica extras: adiciona aos acessos com cores por turno
			aplicar_extras(data.value)
			# Aplica férias e licenças: movem de acessos para colunas específicas
			aplicar_ferias(data.value)
			aplicar_licencas(data.value)
			# Preenche OBLL para a data
			preencher_coluna_obll(data.value)
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
					#bgcolor=ft.Colors.LIGHT_GREEN,
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
					bgcolor=ft.Colors.INDIGO_200,
					width = 120,
					alignment = ft.alignment.center,
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

