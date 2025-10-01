import flet as ft
import datetime
from .base_screen import BaseScreen
from database.database_manager import DatabaseManager
import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
import re


class DisponibilidadeExtrasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "disponibilidade_extras"
        self.selected_opcao = "Rotina"
        self.selected_interticio = "set/out-25"
        # DB
        self.db = DatabaseManager()

    def get_content(self) -> ft.Control:
        titulo = ft.Text(
            "Consulte a disponibilidade para extras",
            size=24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )

        def _sanitize_component(s: str) -> str:
            s = str(s or "").strip()
            # Substitui caracteres inválidos para nomes de arquivo no Windows
            return re.sub(r"[\\/:*?\"<>|]+", "-", s)

        def exportar_pdf(e):
            try:
                # Recalcula as linhas baseadas nos filtros atuais
                linhas = calcular_disponibilidade(dropdown_opcao.value, dropdown_interticio.value)
                # Monta dados da tabela para o PDF
                data_rows = [["Data", "Tipo", "Turno", "Quantidade"]]
                for it in linhas:
                    data_rows.append([
                        str(it.get("data", "")),
                        str(it.get("tipo", "")),
                        str(it.get("turno", "")),
                        str(it.get("qtd", "")),
                    ])

                # Caminho do PDF (mesma estratégia da tela de férias)
                try:
                    db_mgr = self.app.db if hasattr(self.app, 'db') else DatabaseManager()
                except Exception:
                    db_mgr = DatabaseManager()
                base_dir = db_mgr.get_root_path("save_path")
                if not base_dir or not os.path.isdir(base_dir):
                    base_dir = getattr(self.app, "output_dir", None) if hasattr(self, 'app') else None
                if not base_dir or not os.path.isdir(base_dir):
                    base_dir = os.getcwd()
                os.makedirs(base_dir, exist_ok=True)

                opcao = _sanitize_component(dropdown_opcao.value)
                intert = _sanitize_component(dropdown_interticio.value)
                pdf_filename = f"disponibilidade_extras_{opcao}_{intert}.pdf"
                pdf_path = os.path.join(base_dir, pdf_filename)

                doc = SimpleDocTemplate(
                    pdf_path,
                    pagesize=A4,
                    rightMargin=1.5*cm,
                    leftMargin=1.5*cm,
                    topMargin=1.5*cm,
                    bottomMargin=1.5*cm,
                )

                elements = []

                # Cabeçalho com logo
                logo_path = os.path.abspath("assets/icons/logoNUVIG.png")
                if os.path.exists(logo_path):
                    img = Image(logo_path, width=4*cm, height=3*cm)
                    img.hAlign = 'CENTER'
                    elements.append(img)
                elements.append(Spacer(1, 0.5*cm))

                # Título
                titulo_txt = f"Disponibilidade de Extras — {opcao} — {intert}"
                styles = getSampleStyleSheet()
                elements.append(Paragraph(titulo_txt, styles['Title']))
                elements.append(Spacer(1, 0.5*cm))

                # Tabela
                t = Table(data_rows, hAlign='CENTER')
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 10),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ]))
                elements.append(t)

                doc.build(elements)

                # Alert de sucesso
                page = getattr(e, 'page', None) or getattr(getattr(e, 'control', None), 'page', None) or self.page
                if page:
                    dlg = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Sucesso"),
                        content=ft.Text(f"PDF salvo com sucesso em:\n{pdf_path}"),
                        actions=[ft.TextButton("OK", on_click=lambda ev: page.close(dlg))],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.open(dlg)
                    page.update()
            except Exception as ex:
                print("[Extras][exportar_pdf][EXCEPTION]", ex)

        def exportar_texto(e):
            try:
                linhas = calcular_disponibilidade(dropdown_opcao.value, dropdown_interticio.value)
                opcao_atual = str(dropdown_opcao.value or "")
                # Agrupar por data -> {data: {chave: qtd}}
                # Para Rotina: chaves 'diurno'/'noturno'
                # Para OBLL: chave única 'obll'
                por_data = {}
                for it in linhas:
                    data = str(it.get('data', ''))
                    tipo = str(it.get('tipo', '')).lower()
                    turno = str(it.get('turno', '')).lower()
                    qtd = int(it.get('qtd', 0) or 0)
                    if qtd <= 0 or not data:
                        continue
                    if tipo == 'obll' or opcao_atual == 'OBLL':
                        chave = 'obll'
                    else:
                        chave = turno  # 'diurno' ou 'noturno'
                    por_data.setdefault(data, {}).setdefault(chave, 0)
                    por_data[data][chave] += qtd

                # Cabeçalho
                intert_raw = dropdown_interticio.value  # ex: set/out-25
                if intert_raw and '-' in intert_raw:
                    meses_part, ano_part = intert_raw.split('-', 1)
                    meses_fmt = "/".join([m.capitalize() for m in (meses_part or '').split('/') if m])
                    intert_fmt = f"{meses_fmt}-{ano_part}"
                else:
                    intert_fmt = intert_raw

                linhas_txt = []
                linhas_txt.append("Extras NUVIG")
                linhas_txt.append(f"Vagas Disponíveis - {opcao_atual}")
                if intert_fmt:
                    linhas_txt.append(f"(INTERSTÍCIO {intert_fmt})")
                linhas_txt.append("")

                # Ordenar datas dd/mm/YYYY corretamente: converter para datetime para ordenar
                def parse_ddmmyyyy(s):
                    try:
                        return datetime.datetime.strptime(s, "%d/%m/%Y")
                    except Exception:
                        return datetime.datetime.max
                for data in sorted(por_data.keys(), key=parse_ddmmyyyy):
                    linhas_txt.append(f"Dia {data}")
                    turnos = por_data[data]
                    # Diurno
                    if 'diurno' in turnos and turnos['diurno'] > 0:
                        linhas_txt.append("Diurna:")
                        for i in range(1, turnos['diurno'] + 1):
                            linhas_txt.append(f"{i}-")
                        linhas_txt.append("")
                    # Noturno
                    if 'noturno' in turnos and turnos['noturno'] > 0:
                        linhas_txt.append("Noturna:")
                        for i in range(1, turnos['noturno'] + 1):
                            linhas_txt.append(f"{i}-")
                        linhas_txt.append("")
                    # OBLL (se existir nas linhas)
                    if 'obll' in turnos and turnos['obll'] > 0:
                        linhas_txt.append("OBLL:")
                        for i in range(1, turnos['obll'] + 1):
                            linhas_txt.append(f"{i}-")
                        linhas_txt.append("")

                conteudo = "\n".join(linhas_txt).strip() + "\n"

                # Diretório igual ao PDF
                try:
                    db_mgr = self.app.db if hasattr(self.app, 'db') else DatabaseManager()
                except Exception:
                    db_mgr = DatabaseManager()
                base_dir = db_mgr.get_root_path("save_path")
                if not base_dir or not os.path.isdir(base_dir):
                    base_dir = getattr(self.app, "output_dir", None) if hasattr(self, 'app') else None
                if not base_dir or not os.path.isdir(base_dir):
                    base_dir = os.getcwd()
                os.makedirs(base_dir, exist_ok=True)

                opcao = _sanitize_component(dropdown_opcao.value)
                intert = _sanitize_component(dropdown_interticio.value)
                txt_filename = f"disponibilidade_extras_{opcao}_{intert}.txt"
                txt_path = os.path.join(base_dir, txt_filename)
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo)

                page = getattr(e, 'page', None) or getattr(getattr(e, 'control', None), 'page', None) or self.page
                if page:
                    dlg = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Sucesso"),
                        content=ft.Text(f"Texto salvo com sucesso em:\n{txt_path}"),
                        actions=[ft.TextButton("OK", on_click=lambda ev: page.close(dlg))],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.open(dlg)
                    page.update()
            except Exception as ex:
                print("[Extras][exportar_texto][EXCEPTION]", ex)

        # Helpers de data/intertício
        pt_months = {
            "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
            "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
        }

        def parse_interticio_label(label: str) -> tuple[datetime.date, datetime.date]:
            # Formatos como: "set/out-25", "dez/jan-26"
            try:
                meses, ano_suf = label.split("-")
                m1_abbr, m2_abbr = meses.split("/")
                m1 = pt_months[m1_abbr]
                m2 = pt_months[m2_abbr]
                yy = int(ano_suf)
                year2 = 2000 + yy
                # Se cruza o ano (ex: dez/jan-26), m1 pertence ao ano anterior
                if m1 > m2:
                    year1 = year2 - 1
                else:
                    year1 = year2
                start = datetime.date(year1, m1, 21)
                end = datetime.date(year2, m2, 20)
                return start, end
            except Exception:
                # Fallback: mês atual 21 até próximo mês 20
                today = datetime.date.today()
                start = datetime.date(today.year, today.month, 21)
                # próximo mês
                if today.month == 12:
                    end = datetime.date(today.year + 1, 1, 20)
                else:
                    end = datetime.date(today.year, today.month + 1, 20)
                return start, end

        def daterange(start_date: datetime.date, end_date: datetime.date):
            for n in range((end_date - start_date).days + 1):
                yield start_date + datetime.timedelta(days=n)

        def yyyymmdd(d: datetime.date) -> str:
            return d.strftime("%Y-%m-%d")

        def ddmmyyyy(d: datetime.date) -> str:
            return d.strftime("%d/%m/%Y")

        def load_escala_for_date(date_iso: str) -> dict:
            rows = self.db.execute_query("SELECT escala FROM calendario WHERE data = ?", (date_iso,))
            if not rows:
                return {}
            try:
                raw = rows[0]["escala"] if "escala" in rows[0].keys() else rows[0][0]
            except Exception:
                raw = rows[0][0]
            if not raw:
                return {}
            try:
                return json.loads(raw)
            except Exception:
                return {}

        def compute_vagas_por_data(d: datetime.date) -> dict:
            # Capacidades
            cap_diurno = 11
            cap_noturno = 14
            cap_obll = 2
            dados = load_escala_for_date(yyyymmdd(d))

            # Processar acessos (Acesso 01..03)
            acessos = ["Acesso 01", "Acesso 02", "Acesso 03"]
            for col in acessos:
                for pol in dados.get(col, []):
                    status = pol.get("status", "")
                    # Regra 2: Plantão/Compensação/Permuta contam 24h
                    if status in ("Plantão", "Compensação", "Permuta", "Acordo de conduta", "Acordo de Conduta"):
                        cap_diurno -= 1
                        cap_noturno -= 1
                    elif status == "Extra diurno":
                        cap_diurno -= 1
                    elif status == "Extra noturno":
                        cap_noturno -= 1

            # OBLL
            obll_ocupadas = len(dados.get("OBLL", []))
            cap_obll -= obll_ocupadas

            # Não permitir negativos
            cap_diurno = max(0, cap_diurno)
            cap_noturno = max(0, cap_noturno)
            cap_obll = max(0, cap_obll)
            return {
                "diurno": cap_diurno,
                "noturno": cap_noturno,
                "obll": cap_obll,
            }

        def calcular_disponibilidade(opcao: str, interticio_label: str) -> list[dict]:
            inicio, fim = parse_interticio_label(interticio_label)
            linhas = []

            if opcao == "OBLL":
                # 1) Inicializa mapa de todas as datas do intertício com 0 ocupadas
                mapa_ocupadas = {}
                for d in daterange(inicio, fim):
                    mapa_ocupadas[yyyymmdd(d)] = 0

                # 2) Busca na tabela extras as OBLL do intertício selecionado, agrupadas por data
                try:
                    query = (
                        "SELECT c.data AS data, COUNT(*) AS qtd "
                        "FROM extras e "
                        "JOIN calendario c ON e.data_id = c.id "
                        "WHERE e.operacao = 'OBLL' AND e.interticio = ? "
                        "AND date(c.data) BETWEEN date(?) AND date(?) "
                        "GROUP BY c.data"
                    )
                    rows = self.db.execute_query(query, (interticio_label, yyyymmdd(inicio), yyyymmdd(fim)))
                    for row in rows:
                        data_iso = row["data"] if (hasattr(row, "keys") and "data" in row.keys()) else row[0]
                        qtd = row["qtd"] if (hasattr(row, "keys") and "qtd" in row.keys()) else row[1]
                        mapa_ocupadas[data_iso] = int(qtd) if qtd is not None else 0
                except Exception as ex:
                    print(f"[Disponibilidade][OBLL] Falha ao consultar extras: {ex}")

                # 3) Converte para linhas com vagas restantes (máximo 2 por dia)
                for d in daterange(inicio, fim):
                    data_iso = yyyymmdd(d)
                    ocupadas = mapa_ocupadas.get(data_iso, 0)
                    vagas_rest = max(0, 2 - ocupadas)
                    if vagas_rest > 0:
                        linhas.append({
                            "data": ddmmyyyy(d),
                            "tipo": "OBLL",
                            "turno": "vespertino",
                            "qtd": vagas_rest,
                        })
                return linhas

            # Rotina (Diurno/Noturno) – ETAPA 1: base por equipe
            for d in daterange(inicio, fim):
                data_iso = yyyymmdd(d)
                # 1) obter equipe do calendário
                equipe = None
                try:
                    rows_eq = self.db.execute_query("SELECT equipe FROM calendario WHERE data = ? LIMIT 1", (data_iso,))
                    if rows_eq:
                        equipe = rows_eq[0]["equipe"] if (hasattr(rows_eq[0], "keys") and "equipe" in rows_eq[0].keys()) else rows_eq[0][0]
                except Exception as ex:
                    print(f"[Rotina] Falha ao obter equipe para {data_iso}: {ex}")
                    equipe = None

                # 2) contar policiais da equipe (plantão base 24h)
                base_presentes = 0
                equipe_policiais = []
                if equipe:
                    try:
                        rows_pol = self.db.execute_query("SELECT id, qra, nome FROM policiais WHERE escala = ? AND unidade = 'NUVIG'", (equipe,))
                        equipe_policiais = [
                            (row["id"] if hasattr(row, "keys") else row[0],
                             (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                             (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                            for row in rows_pol
                        ] if rows_pol else []
                        base_presentes = len(equipe_policiais)
                    except Exception as ex:
                        print(f"[Rotina] Falha ao contar policiais da equipe {equipe}: {ex}")
                print("\n========== [Rotina][Etapa 1] ==========")
                print(f"Data: {ddmmyyyy(d)}  (ISO: {data_iso})")
                print(f"Equipe do dia: {equipe or '-'}")
                print(f"Policiais da equipe (plantão base 24h) [{base_presentes}]: {[qra or nome for _, qra, nome in equipe_policiais]}")

                # 3) ETAPA 2: reduzir por licenças (policiais da equipe em licença na data)
                licencas_count = 0
                licencas_det = []
                if equipe:
                    try:
                        q_lic = (
                            "SELECT COUNT(*) AS qtd "
                            "FROM licencas l "
                            "JOIN policiais p ON l.policial_id = p.id "
                            "WHERE p.escala = ? AND p.unidade = 'NUVIG' "
                            "AND date(?) BETWEEN date(l.inicio) AND date(l.fim)"
                        )
                        res_lic = self.db.execute_query(q_lic, (equipe, data_iso))
                        if res_lic:
                            licencas_count = res_lic[0]["qtd"] if (hasattr(res_lic[0], "keys") and "qtd" in res_lic[0].keys()) else res_lic[0][0]
                            licencas_count = int(licencas_count) if licencas_count is not None else 0

                        # Detalhar quem está de licença
                        q_lic_det = (
                            "SELECT p.id, p.qra, p.nome "
                            "FROM licencas l JOIN policiais p ON l.policial_id = p.id "
                            "WHERE p.escala = ? AND p.unidade = 'NUVIG' AND date(?) BETWEEN date(l.inicio) AND date(l.fim)"
                        )
                        rows_lic = self.db.execute_query(q_lic_det, (equipe, data_iso))
                        licencas_det = [
                            (row["id"] if hasattr(row, "keys") else row[0],
                             (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                             (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                            for row in rows_lic
                        ] if rows_lic else []
                    except Exception as ex:
                        print(f"[Rotina] Falha ao consultar licenças para {data_iso}/equipe {equipe}: {ex}")
                print("[Rotina][Etapa 2] Licenças encontradas:", [qra or nome for _, qra, nome in licencas_det], f"(total={licencas_count})")

                # 4) ETAPA 3: reduzir por férias (qualquer um dos 3 períodos cobre a data)
                ferias_count = 0
                ferias_det = []
                if equipe:
                    try:
                        q_fer = (
                            "SELECT COUNT(*) AS qtd "
                            "FROM ferias f "
                            "JOIN policiais p ON f.policial_id = p.id "
                            "WHERE p.escala = ? AND p.unidade = 'NUVIG' AND ("
                            "    (f.inicio1 IS NOT NULL AND f.fim1 IS NOT NULL AND date(?) BETWEEN date(f.inicio1) AND date(f.fim1)) OR "
                            "    (f.inicio2 IS NOT NULL AND f.fim2 IS NOT NULL AND date(?) BETWEEN date(f.inicio2) AND date(f.fim2)) OR "
                            "    (f.inicio3 IS NOT NULL AND f.fim3 IS NOT NULL AND date(?) BETWEEN date(f.inicio3) AND date(f.fim3)) "
                            ")"
                        )
                        res_fer = self.db.execute_query(q_fer, (equipe, data_iso, data_iso, data_iso))
                        if res_fer:
                            ferias_count = res_fer[0]["qtd"] if (hasattr(res_fer[0], "keys") and "qtd" in res_fer[0].keys()) else res_fer[0][0]
                            ferias_count = int(ferias_count) if ferias_count is not None else 0

                        q_fer_det = (
                            "SELECT p.id, p.qra, p.nome "
                            "FROM ferias f JOIN policiais p ON f.policial_id = p.id "
                            "WHERE p.escala = ? AND p.unidade = 'NUVIG' AND ("
                            "    (f.inicio1 IS NOT NULL AND f.fim1 IS NOT NULL AND date(?) BETWEEN date(f.inicio1) AND date(f.fim1)) OR "
                            "    (f.inicio2 IS NOT NULL AND f.fim2 IS NOT NULL AND date(?) BETWEEN date(f.inicio2) AND date(f.fim2)) OR "
                            "    (f.inicio3 IS NOT NULL AND f.fim3 IS NOT NULL AND date(?) BETWEEN date(f.inicio3) AND date(f.fim3)) "
                            ")"
                        )
                        rows_fer = self.db.execute_query(q_fer_det, (equipe, data_iso, data_iso, data_iso))
                        ferias_det = [
                            (row["id"] if hasattr(row, "keys") else row[0],
                             (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                             (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                            for row in rows_fer
                        ] if rows_fer else []
                    except Exception as ex:
                        print(f"[Rotina] Falha ao consultar férias para {data_iso}/equipe {equipe}: {ex}")
                print("[Rotina][Etapa 3] Férias encontradas:", [qra or nome for _, qra, nome in ferias_det], f"(total={ferias_count})")

                # 5) ETAPA 4: compensações (24h)
                comp_add = 0
                comp_add_det = []
                comp_sub = 0
                comp_sub_det = []
                try:
                    # Policiais que DEVEM trabalhar na data (somam 24h)
                    q_comp_add = (
                        "SELECT p.id, p.qra, p.nome "
                        "FROM compensacoes c JOIN policiais p ON c.policial_id = p.id "
                        "WHERE p.unidade = 'NUVIG' AND date(c.compensacao) = date(?)"
                    )
                    rows_cadd = self.db.execute_query(q_comp_add, (data_iso,))
                    comp_add_det = [
                        (row["id"] if hasattr(row, "keys") else row[0],
                         (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                         (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                        for row in rows_cadd
                    ] if rows_cadd else []
                    comp_add = len(comp_add_det)

                    # Policiais que NÃO devem trabalhar na data (a compensar) e que estariam de plantão
                    # Removem 24h da base somente se p.escala == equipe do dia
                    if equipe:
                        q_comp_sub = (
                            "SELECT p.id, p.qra, p.nome "
                            "FROM compensacoes c JOIN policiais p ON c.policial_id = p.id "
                            "WHERE p.unidade = 'NUVIG' AND p.escala = ? AND date(c.a_compensar) = date(?)"
                        )
                        rows_csub = self.db.execute_query(q_comp_sub, (equipe, data_iso))
                        comp_sub_det = [
                            (row["id"] if hasattr(row, "keys") else row[0],
                             (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                             (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                            for row in rows_csub
                        ] if rows_csub else []
                        comp_sub = len(comp_sub_det)
                except Exception as ex:
                    print(f"[Rotina] Falha ao consultar compensações para {data_iso}: {ex}")

                print("[Rotina][Etapa 4] Compensações +24h:", [qra or nome for _, qra, nome in comp_add_det], f"(total={comp_add})")
                print("[Rotina][Etapa 4] Compensações -24h (a compensar da equipe):", [qra or nome for _, qra, nome in comp_sub_det], f"(total={comp_sub})")

                ajustes_24h = comp_add - comp_sub   # Aplicado em ambos turnos
                # 6) ETAPA 5: permutas (24h)
                perm_add = 0
                perm_sub = 0
                perm_add_det = []
                perm_sub_det = []
                try:
                    # Caso A: data == data_permutado -> entra SOLICITANTE (+)
                    q_perm_add1 = (
                        "SELECT p.id, p.qra, p.nome "
                        "FROM permutas pm JOIN policiais p ON pm.solicitante = p.id "
                        "WHERE p.unidade = 'NUVIG' AND date(pm.data_permutado) = date(?)"
                    )
                    rows_pa1 = self.db.execute_query(q_perm_add1, (data_iso,))
                    perm_add_det += [
                        (row["id"] if hasattr(row, "keys") else row[0],
                         (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                         (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                        for row in (rows_pa1 or [])
                    ]

                    # Caso A: data == data_permutado -> sai PERMUTADO (-) se estaria de plantão
                    if equipe:
                        q_perm_sub1 = (
                            "SELECT p.id, p.qra, p.nome "
                            "FROM permutas pm JOIN policiais p ON pm.permutado = p.id "
                            "WHERE p.unidade = 'NUVIG' AND p.escala = ? AND date(pm.data_permutado) = date(?)"
                        )
                        rows_ps1 = self.db.execute_query(q_perm_sub1, (equipe, data_iso))
                        perm_sub_det += [
                            (row["id"] if hasattr(row, "keys") else row[0],
                             (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                             (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                            for row in (rows_ps1 or [])
                        ]

                    # Caso B: data == data_solicitante -> entra PERMUTADO (+)
                    q_perm_add2 = (
                        "SELECT p.id, p.qra, p.nome "
                        "FROM permutas pm JOIN policiais p ON pm.permutado = p.id "
                        "WHERE p.unidade = 'NUVIG' AND date(pm.data_solicitante) = date(?)"
                    )
                    rows_pa2 = self.db.execute_query(q_perm_add2, (data_iso,))
                    perm_add_det += [
                        (row["id"] if hasattr(row, "keys") else row[0],
                         (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                         (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                        for row in (rows_pa2 or [])
                    ]

                    # Caso B: data == data_solicitante -> sai SOLICITANTE (-) se estaria de plantão
                    if equipe:
                        q_perm_sub2 = (
                            "SELECT p.id, p.qra, p.nome "
                            "FROM permutas pm JOIN policiais p ON pm.solicitante = p.id "
                            "WHERE p.unidade = 'NUVIG' AND p.escala = ? AND date(pm.data_solicitante) = date(?)"
                        )
                        rows_ps2 = self.db.execute_query(q_perm_sub2, (equipe, data_iso))
                        perm_sub_det += [
                            (row["id"] if hasattr(row, "keys") else row[0],
                             (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                             (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                            for row in (rows_ps2 or [])
                        ]

                    perm_add = len(perm_add_det)
                    perm_sub = len(perm_sub_det)
                except Exception as ex:
                    print(f"[Rotina] Falha ao consultar permutas para {data_iso}: {ex}")

                print("[Rotina][Etapa 5] Permutas +24h:", [qra or nome for _, qra, nome in perm_add_det], f"(total={perm_add})")
                print("[Rotina][Etapa 5] Permutas -24h (da equipe):", [qra or nome for _, qra, nome in perm_sub_det], f"(total={perm_sub})")

                # 7) ETAPA 6: acordo de conduta (24h)
                conduta_add = 0
                conduta_det = []
                try:
                    q_cond = (
                        "SELECT p.id, p.qra, p.nome "
                        "FROM tacs c JOIN policiais p ON c.policial_id = p.id "
                        "WHERE p.unidade = 'NUVIG' AND date(c.data) = date(?)"
                    )
                    rows_cond = self.db.execute_query(q_cond, (data_iso,))
                    conduta_det = [
                        (row["id"] if hasattr(row, "keys") else row[0],
                         (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                         (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                        for row in (rows_cond or [])
                    ]
                    conduta_add = len(conduta_det)
                except Exception as ex:
                    print(f"[Rotina] Falha ao consultar conduta para {data_iso}: {ex}")
                print("[Rotina][Etapa 6] Conduta +24h:", [qra or nome for _, qra, nome in conduta_det], f"(total={conduta_add})")

                # 8) ETAPA 7: extras por turno (Rotina)
                extras_diurno = 0
                extras_noturno = 0
                extras_d_det = []
                extras_n_det = []
                try:
                    q_extra_d = (
                        "SELECT p.id, p.qra, p.nome "
                        "FROM extras e "
                        "JOIN policiais p ON e.policial_id = p.id "
                        "JOIN calendario c ON e.data_id = c.id "
                        "WHERE e.operacao = 'Rotina' AND e.turno = 'Diurno' AND date(c.data) = date(?)"
                    )
                    rows_ed = self.db.execute_query(q_extra_d, (data_iso,))
                    extras_d_det = [
                        (row["id"] if hasattr(row, "keys") else row[0],
                         (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                         (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                        for row in (rows_ed or [])
                    ]
                    extras_diurno = len(extras_d_det)

                    q_extra_n = (
                        "SELECT p.id, p.qra, p.nome "
                        "FROM extras e "
                        "JOIN policiais p ON e.policial_id = p.id "
                        "JOIN calendario c ON e.data_id = c.id "
                        "WHERE e.operacao = 'Rotina' AND e.turno = 'Noturno' AND date(c.data) = date(?)"
                    )
                    rows_en = self.db.execute_query(q_extra_n, (data_iso,))
                    extras_n_det = [
                        (row["id"] if hasattr(row, "keys") else row[0],
                         (row["qra"] if hasattr(row, "keys") else row[1]) or "",
                         (row["nome"] if hasattr(row, "keys") else row[2]) or "")
                        for row in (rows_en or [])
                    ]
                    extras_noturno = len(extras_n_det)
                except Exception as ex:
                    print(f"[Rotina] Falha ao consultar extras (Rotina) para {data_iso}: {ex}")
                print("[Rotina][Etapa 7] Extras Diurno:", [qra or nome for _, qra, nome in extras_d_det], f"(total={extras_diurno})")
                print("[Rotina][Etapa 7] Extras Noturno:", [qra or nome for _, qra, nome in extras_n_det], f"(total={extras_noturno})")

                base_ajustada = max(0, base_presentes - licencas_count - ferias_count)
                ajustes_24h_total = ajustes_24h + (perm_add - perm_sub) + conduta_add

                # 9) ETAPA 8: retirar 'Administrativo' que foram adicionados
                # Conjuntos de IDs
                base_ids = {pid for (pid, _, _) in equipe_policiais}
                lic_ids = {pid for (pid, _, _) in licencas_det}
                fer_ids = {pid for (pid, _, _) in ferias_det}
                comp_sub_ids = {pid for (pid, _, _) in comp_sub_det}
                perm_sub_ids = {pid for (pid, _, _) in perm_sub_det}
                already_removed_ids = lic_ids | fer_ids | comp_sub_ids | perm_sub_ids

                add24_ids = {pid for (pid, _, _) in comp_add_det} | {pid for (pid, _, _) in perm_add_det} | {pid for (pid, _, _) in conduta_det}
                extras_d_ids = {pid for (pid, _, _) in extras_d_det}
                extras_n_ids = {pid for (pid, _, _) in extras_n_det}

                check_ids = list((base_ids | add24_ids | extras_d_ids | extras_n_ids))
                admins_set = set()
                if check_ids:
                    placeholders = ",".join(["?"] * len(check_ids))
                    q_admins = f"SELECT id FROM policiais WHERE funcao = 'Administrativo' AND id IN ({placeholders})"
                    try:
                        rows_admins = self.db.execute_query(q_admins, tuple(check_ids))
                        admins_set = {row["id"] if hasattr(row, "keys") else row[0] for row in (rows_admins or [])}
                    except Exception as ex:
                        print(f"[Rotina] Falha ao consultar função Administrativo: {ex}")

                # Remoções por categoria
                admins_in_base = (base_ids & admins_set) - already_removed_ids
                admins_in_add24 = add24_ids & admins_set
                admins_in_extras_d = extras_d_ids & admins_set
                admins_in_extras_n = extras_n_ids & admins_set

                # Map helper: id -> label (QRA or Nome)
                def id_label_map(rows):
                    return {pid: (qra or nome) for (pid, qra, nome) in rows}

                map_base = id_label_map(equipe_policiais)
                map_comp_add = id_label_map(comp_add_det)
                map_perm_add = id_label_map(perm_add_det)
                map_cond = id_label_map(conduta_det)
                map_extra_d = id_label_map(extras_d_det)
                map_extra_n = id_label_map(extras_n_det)

                if admins_in_base:
                    base_ajustada = max(0, base_ajustada - len(admins_in_base))
                if admins_in_add24:
                    ajustes_24h_total = max(0, ajustes_24h_total - len(admins_in_add24))
                if admins_in_extras_d:
                    extras_diurno = max(0, extras_diurno - len(admins_in_extras_d))
                if admins_in_extras_n:
                    extras_noturno = max(0, extras_noturno - len(admins_in_extras_n))

                # Build readable labels
                base_labels = [map_base.get(i) for i in admins_in_base]
                add24_labels = [map_comp_add.get(i) or map_perm_add.get(i) or map_cond.get(i) for i in admins_in_add24]
                extras_d_labels = [map_extra_d.get(i) for i in admins_in_extras_d]
                extras_n_labels = [map_extra_n.get(i) for i in admins_in_extras_n]

                print("[Rotina][Etapa 8] Administrativo removido:")
                print("  Base:", base_labels)
                print("  +24h:", add24_labels)
                print("  Extras D:", extras_d_labels)
                print("  Extras N:", extras_n_labels)

                # Final: computar presentes
                presentes_diurno = base_ajustada + ajustes_24h_total + extras_diurno
                presentes_noturno = base_ajustada + ajustes_24h_total + extras_noturno

                vagas_diurno = max(0, 11 - presentes_diurno)
                vagas_noturno = max(0, 14 - presentes_noturno)

                print("[Rotina][Totais]")
                print(f"  Base (equipe)           : {base_presentes}")
                print(f"  (-) Licenças            : {licencas_count}")
                print(f"  (-) Férias              : {ferias_count}")
                print(f"  (=) Base ajustada       : {base_ajustada}")
                print(f"  (+) Ajustes 24h (comp)  : {ajustes_24h}  [+{comp_add} / -{comp_sub}]")
                print(f"  (+) Ajustes 24h (perm)  : {perm_add - perm_sub}  [+{perm_add} / -{perm_sub}]")
                print(f"  (+) Ajustes 24h (cond)  : {conduta_add}")
                print(f"  (+) Extras diurno       : {extras_diurno}")
                print(f"  (+) Extras noturno      : {extras_noturno}")
                print(f"  Disponíveis diurno      : {presentes_diurno} | Necessários: 11 | Vagas: {vagas_diurno}")
                print(f"  Disponíveis noturno     : {presentes_noturno} | Necessários: 14 | Vagas: {vagas_noturno}")

                if vagas_diurno > 0:
                    linhas.append({
                        "data": ddmmyyyy(d),
                        "tipo": "Rotina",
                        "turno": "diurno",
                        "qtd": vagas_diurno,
                    })
                if vagas_noturno > 0:
                    linhas.append({
                        "data": ddmmyyyy(d),
                        "tipo": "Rotina",
                        "turno": "noturno",
                        "qtd": vagas_noturno,
                    })
            return linhas

        def render_tabela(linhas: list[dict]):
            # Retorna uma lista de Controls para inserir em um ListView (scrollável)
            controls: list[ft.Control] = []
            header = ft.Row([
                ft.Container(ft.Text("Data", weight=ft.FontWeight.BOLD), width=200),
                ft.Container(ft.Text("Tipo", weight=ft.FontWeight.BOLD), width=200),
                ft.Container(ft.Text("Turno", weight=ft.FontWeight.BOLD), width=200),
                ft.Container(ft.Text("Quantidade", weight=ft.FontWeight.BOLD), width=200),
            ], alignment=ft.MainAxisAlignment.START)
            controls.append(header)

            if not linhas:
                controls.append(ft.Text("Nenhuma disponibilidade encontrada para o período selecionado.", size=16))
                return controls

            for item in linhas:
                row = ft.Row([
                    ft.Container(ft.Text(item["data"]), width=200),
                    ft.Container(ft.Text(item["tipo"]), width=200),
                    ft.Container(ft.Text(item["turno"]), width=200),
                    ft.Container(ft.Text(str(item["qtd"])) , width=200),
                ], alignment=ft.MainAxisAlignment.START)
                # divisor visual
                controls.append(row)
                controls.append(ft.Divider(height=1))
            return controls

        def atualizar_tabela(e=None):
            linhas = calcular_disponibilidade(dropdown_opcao.value, dropdown_interticio.value)
            controls = render_tabela(linhas)
            tabela_scroll.controls = controls
            # Garantir update
            try:
                page = getattr(e, "page", None) or getattr(getattr(e, "control", None), "page", None) or self.page
                if page:
                    page.update()
            except Exception:
                pass

        dropdown_opcao = ft.Dropdown(
            options=[
                ft.dropdown.Option("Rotina"),
                ft.dropdown.Option("OBLL"),
            ],
            bgcolor=ft.Colors.WHITE,
            value=self.selected_opcao,
            width=180,
            on_change=atualizar_tabela,
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
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
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
            e.control.page.update()

        def on_date_change(e):
            # disparado ao selecionar data no DatePicker
            if datepicker.value:
                ddmmyyyy = datepicker.value.strftime("%d/%m/%Y")
                data.value = ddmmyyyy
                data.cursor_position = len(data.value)
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
            width=180,
            height=47,
            on_click=open_date_picker
        )


        data = ft.TextField(label="Data", width=btn_data.width, hint_text="dd/mm/aaaa", bgcolor=ft.Colors.WHITE)
        data.on_change = mascara_data

        interticio_options = options = [
                    ft.dropdown.Option("set/out-25"),
                    ft.dropdown.Option("out/nov-25"),
                    ft.dropdown.Option("nov/dez-25"),
                    ft.dropdown.Option("dez/jan-26"),
                    ft.dropdown.Option("jan/fev-26"),
                    ft.dropdown.Option("fev/mar-26"),
                    ft.dropdown.Option("mar/abr-26"),
                    ft.dropdown.Option("abr/mai-26"),
                    ft.dropdown.Option("mai/jun-26"),
                    ft.dropdown.Option("jun/jul-26"),
                    ft.dropdown.Option("jul/ago-26"),
                    ft.dropdown.Option("ago/set-26"),
                    ft.dropdown.Option("set/out-26"),
                    ft.dropdown.Option("out/nov-26"),
                    ft.dropdown.Option("nov/dez-26"),
                    ]

        dropdown_interticio = ft.Dropdown(
            options=interticio_options,
            bgcolor=ft.Colors.WHITE,
            value=self.selected_interticio,
            width=180,
            on_change=atualizar_tabela,
        )

        row_dropdowns = ft.Row(
            controls=[dropdown_opcao, dropdown_interticio],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=30,
        )

        tabela_scroll = ft.ListView(
            controls=[ft.Text("Tabela de disponibilidade será exibida aqui.", size=16)],
            expand=False,
            auto_scroll=False,
            width=800,
            height=500,
        )

        # Container para centralizar e fixar largura em 800px
        tabela_container = ft.Container(content=tabela_scroll, width=800, alignment=ft.alignment.center)

        btn_export = ft.ElevatedButton(
            text="Exportar PDF",
            icon=ft.Icons.PICTURE_AS_PDF,
            width=200,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.BLACK),
            ),
            tooltip="Exportar pdf do relatório de disponibilidade de extras",
            on_click=exportar_pdf
        )
        btn_texto = ft.ElevatedButton(
            text="Texto para Whatsapp",
            icon=ft.Icons.TELEGRAM,
            width=btn_export.width,
            bgcolor=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                color=ft.Colors.BLACK,
                text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(1, ft.Colors.BLACK),
            ),
            tooltip="Exportar texdo para Whatsapp",
            on_click=exportar_texto
        )

        row_buttons = ft.Row(controls=[btn_export, btn_texto],
                             alignment=ft.MainAxisAlignment.CENTER)

        main_column = ft.Column(
            controls=[
                titulo,
                row_dropdowns,
                ft.Container(height=30),
                tabela_container,
                ft.Container(height=30),
                row_buttons
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
        # Render inicial
        tabela_scroll.controls = [ft.Text("Carregando disponibilidade...")]
        # Disparar cálculo inicial após montar controles
        try:
            linhas_inic = calcular_disponibilidade(dropdown_opcao.value, dropdown_interticio.value)
            tabela_scroll.controls = render_tabela(linhas_inic)
        except Exception:
            pass
        return main_column
