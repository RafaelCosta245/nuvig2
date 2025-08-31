import sqlite3
import os
from typing import Optional, List, Dict, Any

class DatabaseManager:
    def get_equipe_by_data(self, data: str) -> Optional[str]:
        """Busca o valor da equipe na tabela calendario para uma data específica (aaaa-mm-dd)"""
        try:
            query = "SELECT equipe FROM calendario WHERE data = ?"
            results = self.execute_query(query, (data,))
            if results:
                return results[0]["equipe"]
            return None
        except Exception as e:
            print(f"Erro ao buscar equipe por data: {e}")
            return None

    def get_qras_by_equipe(self, equipe: str) -> list:
        """Busca todos os policiais com escala igual ao valor da equipe e retorna os qras"""
        try:
            query = "SELECT qra FROM policiais WHERE escala = ?"
            results = self.execute_query(query, (equipe,))
            return [row["qra"] for row in results]
        except Exception as e:
            print(f"Erro ao buscar qras por equipe: {e}")
            return []
    def get_policial_by_matricula(self, matricula: str) -> Optional[Dict[str, Any]]:
        """Busca um policial pela matrícula"""
        try:
            query = "SELECT * FROM policiais WHERE matricula = ?"
            results = self.execute_query(query, (matricula,))
            if results:
                return dict(results[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar policial por matrícula: {e}")
            return None

    def atualizar_policial(self, matricula: str, nome: str, cargo: str, lotacao: str) -> bool:
        """Atualiza os dados de um policial pela matrícula"""
        try:
            command = """
                UPDATE policiais SET nome = ?, qra = ?, escala = ? WHERE matricula = ?
            """
            return self.execute_command(command, (nome, cargo, lotacao, matricula))
        except Exception as e:
            print(f"Erro ao atualizar policial: {e}")
            return False
    def __init__(self, db_path: str = "assets/db/nuvig.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.last_error: Optional[str] = None
        
    def init_database(self):
        """Inicializa o banco de dados e cria as tabelas necessárias"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Removido: self._create_tables() para não criar tabelas automaticamente
        # Removido: self._create_tables() para não criar tabelas automaticamente
            print("Banco de dados inicializado com sucesso!")
            
        except sqlite3.Error as e:
            print(f"Erro ao inicializar banco de dados: {e}")
            
    def _create_tables(self):
        """Cria as tabelas do sistema"""
        cursor = self.connection.cursor()
        
        # Tabela de logs de sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                module TEXT,
                severity TEXT DEFAULT 'INFO'
            )
        """)
        
        # Tabela de configurações do sistema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE NOT NULL,
                config_value TEXT,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de acessos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT NOT NULL,
                veiculo TEXT,
                placa TEXT,
                destino TEXT NOT NULL,
                entrada TIMESTAMP NOT NULL,
                saida TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de acessantes (cadastro de pessoas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acessantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                documento TEXT UNIQUE NOT NULL,
                veiculo TEXT,
                placa TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de unidades
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS unidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unidade TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de policiais
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS policiais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                qra TEXT,
                matricula TEXT,
                escala TEXT,
                situacao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inserir configurações padrão
        self._insert_default_configs(cursor)
        
        # Inserir algumas unidades padrão se a tabela estiver vazia
        self._insert_default_units(cursor)
        
        self.connection.commit()
        
    def _insert_default_configs(self, cursor):
        """Insere configurações padrão do sistema"""
        default_configs = [
            ("app_name", "Acesso2", "Nome da aplicação"),
            ("app_version", "1.0.0", "Versão da aplicação"),
            ("theme_mode", "light", "Modo do tema (light/dark)"),
            ("auto_save", "true", "Salvamento automático ativado"),
            ("log_level", "INFO", "Nível de log padrão")
        ]
        
        for key, value, description in default_configs:
            cursor.execute("""
                INSERT OR IGNORE INTO system_config (config_key, config_value, description)
                VALUES (?, ?, ?)
            """, (key, value, description))
            
    def _insert_default_units(self, cursor):
        """Insere unidades padrão se a tabela estiver vazia"""
        # Verificar se a tabela está vazia
        cursor.execute("SELECT COUNT(*) as count FROM unidades")
        count = cursor.fetchone()['count']
        
        if count == 0:
            default_units = [
                "UP 01 - Administração",
                "UP 02 - Recursos Humanos",
                "UP 03 - Financeiro",
                "UP 04 - TI",
                "UP 05 - Manutenção",
                "UP 06 - UPE",
                "UP 07 - Almoxarifado",
                "UP 08 - Segurança",
                "UP 09 - Limpeza",
                "UP 10 - Outros"
            ]
            
            for unidade in default_units:
                cursor.execute("""
                    INSERT OR IGNORE INTO unidades (unidade)
                    VALUES (?)
                """, (unidade,))
        
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Executa uma consulta SELECT e retorna os resultados"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.last_error = None
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro na consulta: {e}")
            self.last_error = str(e)
            return []
            
    def execute_command(self, command: str, params: tuple = ()) -> bool:
        """Executa um comando INSERT, UPDATE ou DELETE"""
        try:
            cursor = self.connection.cursor()
            cursor.execute(command, params)
            self.connection.commit()
            self.last_error = None
            return True
        except sqlite3.Error as e:
            print(f"Erro no comando: {e}")
            self.last_error = str(e)
            return False
            
    def log_system_action(self, action: str, description: str = "", module: str = "", severity: str = "INFO"):
        """Registra uma ação do sistema"""
        command = """
            INSERT INTO system_logs (action, description, module, severity)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_command(command, (action, description, module, severity))
        
    def get_system_config(self, config_key: str) -> Optional[str]:
        """Obtém uma configuração do sistema"""
        query = "SELECT config_value FROM system_config WHERE config_key = ?"
        results = self.execute_query(query, (config_key,))
        return results[0]['config_value'] if results else None
        
    def set_system_config(self, config_key: str, config_value: str, description: str = ""):
        """Define uma configuração do sistema"""
        command = """
            INSERT OR REPLACE INTO system_config (config_key, config_value, description, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        return self.execute_command(command, (config_key, config_value, description))

    # --- Policiais ---
    def inserir_policial(self, nome: str, qra: str, matricula: str, escala: str, situacao: str, inicio: str, unidade: str) -> bool:
        """Insere um policial na tabela policiais"""
        try:
            command = """
                INSERT INTO policiais (nome, qra, matricula, escala, situacao, inicio, unidade)
                VALUES (?, ?, ?, ?, ?, ?,?)
            """
            return self.execute_command(command, (nome, qra, matricula, escala, situacao, inicio, unidade))
        except Exception as e:
            print(f"Erro ao inserir policial: {e}")
            return False
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas básicas do sistema"""
        stats = {}
        
        # Contar logs do sistema
        query = "SELECT COUNT(*) as total FROM system_logs"
        results = self.execute_query(query)
        stats['total_logs'] = results[0]['total'] if results else 0
        
        # Contar configurações
        query = "SELECT COUNT(*) as total FROM system_config"
        results = self.execute_query(query)
        stats['total_configs'] = results[0]['total'] if results else 0
        
        return stats
        
    def buscar_acessante_por_documento(self, documento: str) -> Optional[Dict[str, Any]]:
        """Busca um acessante pelo documento na tabela acessantes"""
        try:
            query = "SELECT nome, veiculo, placa, documento FROM acessantes WHERE documento = ?"
            results = self.execute_query(query, (documento,))
            if results:
                return dict(results[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar acessante por documento: {e}")
            return None
            
    def buscar_acessante_por_placa(self, placa: str) -> Optional[Dict[str, Any]]:
        """Busca um acessante pela placa na tabela acessantes"""
        try:
            query = "SELECT nome, veiculo, placa, documento FROM acessantes WHERE placa = ?"
            results = self.execute_query(query, (placa,))
            if results:
                return dict(results[0])
            return None
        except Exception as e:
            print(f"Erro ao buscar acessante por placa: {e}")
            return None
            
    def inserir_acessante(self, nome: str, documento: str, veiculo: str = "", placa: str = "") -> bool:
        """Insere um novo acessante na tabela acessantes"""
        try:
            command = """
                INSERT OR REPLACE INTO acessantes (nome, documento, veiculo, placa)
                VALUES (?, ?, ?, ?)
            """
            
            return self.execute_command(command, (nome, documento, veiculo, placa))
            
        except Exception as e:
            print(f"Erro ao inserir acessante: {e}")
            return False
            
    def verificar_acessante_existe(self, documento: str) -> bool:
        """Verifica se um acessante já existe pelo documento"""
        try:
            query = "SELECT COUNT(*) as count FROM acessantes WHERE documento = ?"
            results = self.execute_query(query, (documento,))
            return results[0]['count'] > 0 if results else False
        except Exception as e:
            print(f"Erro ao verificar acessante: {e}")
            return False
            
    def buscar_unidades(self) -> List[str]:
        """Busca todas as unidades na tabela unidades"""
        try:
            query = "SELECT unidade FROM unidades ORDER BY unidade"
            results = self.execute_query(query, ())
            return [row['unidade'] for row in results]
        except Exception as e:
            print(f"Erro ao buscar unidades: {e}")
            return []
            
    def buscar_acessos_sem_saida(self) -> List[Dict[str, Any]]:
        """Busca todos os acessos que não possuem saída registrada"""
        try:
            query = """
                SELECT id, nome, documento, veiculo, placa, destino, entrada
                FROM acessos 
                WHERE saida IS NULL OR saida = ''
                ORDER BY entrada DESC
            """
            results = self.execute_query(query, ())
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Erro ao buscar acessos sem saída: {e}")
            return []
            
    def registrar_acesso(self, nome: str, documento: str, veiculo: str, placa: str, destino: str, tipo: str = "entrada") -> bool:
        """Registra um acesso na tabela acessos"""
        try:
            from datetime import datetime
            agora = datetime.now()
            
            command = """
                INSERT INTO acessos (nome, documento, veiculo, placa, destino, entrada)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            
            return self.execute_command(command, (
                nome, documento, veiculo, placa, destino, 
                agora.strftime("%Y-%m-%d %H:%M:%S")
            ))
            
        except Exception as e:
            print(f"Erro ao registrar acesso: {e}")
            return False
            
    def buscar_acesso_para_saida(self, nome: str, documento: str, veiculo: str = "", placa: str = "") -> Optional[Dict[str, Any]]:
        """Busca um acesso ativo (sem saída) para registrar a saída"""
        try:
            # Construir a query baseada nos parâmetros fornecidos
            query = """
                SELECT id, nome, documento, veiculo, placa, destino, entrada
                FROM acessos 
                WHERE (saida IS NULL OR saida = '')
                AND nome = ? AND documento = ?
            """
            params = [nome, documento]
            
            # Adicionar filtros opcionais se fornecidos
            if veiculo:
                query += " AND veiculo = ?"
                params.append(veiculo)
            if placa:
                query += " AND placa = ?"
                params.append(placa)
                
            # Ordenar por ID decrescente para pegar o maior ID (mais recente)
            query += " ORDER BY id DESC LIMIT 1"
            
            results = self.execute_query(query, tuple(params))
            if results:
                return dict(results[0])
            return None
            
        except Exception as e:
            print(f"Erro ao buscar acesso para saída: {e}")
            return None
            
    def registrar_saida(self, acesso_id: int) -> bool:
        """Registra a saída de um acesso específico"""
        try:
            from datetime import datetime
            agora = datetime.now()
            
            command = """
                UPDATE acessos 
                SET saida = ?
                WHERE id = ? AND (saida IS NULL OR saida = '')
            """
            
            sucesso = self.execute_command(command, (
                agora.strftime("%Y-%m-%d %H:%M:%S"),
                acesso_id
            ))
            
            if sucesso:
                print(f"Saída registrada com sucesso para o acesso ID: {acesso_id}")
            else:
                print(f"Erro ao registrar saída para o acesso ID: {acesso_id}")
                
            return sucesso
            
        except Exception as e:
            print(f"Erro ao registrar saída: {e}")
            return False
            
    def buscar_acessos_por_periodo(self, data_inicio: str, hora_inicio: str, data_fim: str, hora_fim: str) -> List[Dict[str, Any]]:
        """Busca acessos dentro de um período específico"""
        try:
            # Converter datas do formato dd/mm/aaaa para aaaa-mm-dd
            def converter_data(data_str: str) -> str:
                if not data_str or len(data_str) < 10:
                    return ""
                partes = data_str.split('/')
                if len(partes) == 3:
                    return f"{partes[2]}-{partes[1]}-{partes[0]}"
                return ""
            
            # Converter horas do formato HH:MM para HH:MM:SS
            def converter_hora(hora_str: str) -> str:
                if not hora_str or len(hora_str) < 5:
                    return "00:00:00"
                return hora_str + ":00"
            
            # Construir as datas completas
            data_inicio_convertida = converter_data(data_inicio)
            data_fim_convertida = converter_data(data_fim)
            hora_inicio_convertida = converter_hora(hora_inicio)
            hora_fim_convertida = converter_hora(hora_fim)
            
            if not data_inicio_convertida or not data_fim_convertida:
                return []
            
            # Construir as datas/horas completas para comparação
            inicio_completo = f"{data_inicio_convertida} {hora_inicio_convertida}"
            fim_completo = f"{data_fim_convertida} {hora_fim_convertida}"
            
            query = """
                SELECT id, nome, documento, veiculo, placa, destino, entrada, saida
                FROM acessos 
                WHERE entrada >= ? AND entrada <= ?
                ORDER BY entrada DESC
            """
            
            results = self.execute_query(query, (inicio_completo, fim_completo))
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Erro ao buscar acessos por período: {e}")
            return []
        
    def close_connection(self):
        """Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.close()
            
    def __del__(self):
        """Destrutor para fechar conexão automaticamente"""
        self.close_connection()
