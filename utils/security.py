import secrets
import string
from typing import Tuple

class SecurityUtils:
    """Utilitários de segurança para o sistema"""
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Gera um token seguro aleatório"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def generate_session_token() -> str:
        """Gera um token de sessão seguro"""
        return SecurityUtils.generate_secure_token(64)
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """Remove caracteres perigosos de uma string de entrada"""
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
        sanitized = input_string
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de e-mail"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """
        Valida formato de nome de arquivo
        Retorna: (é_válido, mensagem_erro)
        """
        if not filename or len(filename.strip()) == 0:
            return False, "Nome de arquivo não pode estar vazio"
        
        if len(filename) > 255:
            return False, "Nome de arquivo muito longo (máximo 255 caracteres)"
        
        # Caracteres inválidos em nomes de arquivo
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in invalid_chars:
            if char in filename:
                return False, f"Nome de arquivo não pode conter o caractere: {char}"
        
        return True, "Nome de arquivo válido"
    
    @staticmethod
    def generate_file_hash(content: str) -> str:
        """Gera um hash simples para verificação de integridade de arquivo"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    @staticmethod
    def validate_json_schema(data: dict, required_fields: list) -> Tuple[bool, str]:
        """
        Valida se um dicionário contém os campos obrigatórios
        Retorna: (é_válido, mensagem_erro)
        """
        for field in required_fields:
            if field not in data:
                return False, f"Campo obrigatório ausente: {field}"
            
            if data[field] is None or (isinstance(data[field], str) and len(data[field].strip()) == 0):
                return False, f"Campo obrigatório vazio: {field}"
        
        return True, "Dados válidos"
