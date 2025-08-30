# Acesso2 - Sistema de Controle de Acesso Desktop

Um sistema desktop desenvolvido em Python usando Flet 0.28 para controle de acesso e gerenciamento de funcionalidades.

## 🚀 Características

- **Interface Desktop**: Aplicação nativa para Windows, macOS e Linux
- **Banco SQLite3**: Armazenamento local de dados e configurações
- **Arquitetura Modular**: Cada tela em arquivo separado para fácil manutenção
- **Interface Moderna**: Design responsivo e intuitivo
- **Logs do Sistema**: Rastreamento completo de atividades
- **Acesso Direto**: Inicia diretamente na tela principal

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Flet 0.28.0
- SQLite3 (incluído no Python)

## 🛠️ Instalação

1. **Clone o repositório:**
```bash
git clone <url-do-repositorio>
cd acesso2
```

2. **Crie um ambiente virtual:**
```bash
python -m venv .venv
```

3. **Ative o ambiente virtual:**
   - **Windows:**
   ```bash
   .venv\Scripts\activate
   ```
   - **macOS/Linux:**
   ```bash
   source .venv/bin/activate
   ```

4. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

## 🚀 Executando o Projeto

```bash
python main.py
```

**O aplicativo iniciará diretamente na tela principal (Home) sem necessidade de login.**

## 📁 Estrutura do Projeto

```
acesso2/
├── main.py                 # Arquivo principal da aplicação
├── requirements.txt        # Dependências do projeto
├── README.md              # Este arquivo
├── config/                # Configurações do sistema
│   └── settings.py        # Configurações e constantes
├── database/              # Gerenciamento do banco de dados
│   └── database_manager.py # Classe principal do banco
├── screens/               # Telas da aplicação
│   ├── base_screen.py     # Classe base para todas as telas
│   └── home_screen.py     # Tela principal
└── utils/                 # Utilitários
    └── security.py        # Funções de segurança
```

## 🎯 Funcionalidades

### Tela Principal (Home)
- Dashboard com funcionalidades principais
- Cards de navegação para módulos
- Estatísticas do sistema em tempo real
- Interface limpa e organizada

## 🗄️ Banco de Dados

O sistema utiliza SQLite3 com as seguintes tabelas:

- **system_logs**: Logs de atividades do sistema
- **system_config**: Configurações e parâmetros do sistema

## 🔒 Segurança

- Sanitização de entrada de dados
- Validação de arquivos e dados
- Logs de auditoria do sistema
- Tokens seguros para funcionalidades

## 🎨 Interface

- Design responsivo
- Tema claro/escuro configurável
- Componentes reutilizáveis
- Ícones intuitivos
- Acesso direto sem autenticação

## 🧪 Desenvolvimento

### Adicionando Novas Telas

1. Crie um novo arquivo em `screens/`
2. Herde de `BaseScreen`
3. Implemente o método `get_view()`
4. Adicione a tela no `main.py`

Exemplo:
```python
from .base_screen import BaseScreen

class NovaTela(BaseScreen):
    def get_view(self) -> ft.View:
        # Implementar interface da tela
        pass
```

### Modificando o Banco de Dados

1. Edite `database/database_manager.py`
2. Adicione novos métodos conforme necessário
3. Atualize as tabelas se necessário

## 📝 Logs

O sistema gera logs para:
- Carregamento de telas
- Ações do usuário
- Configurações do sistema
- Erros e exceções

## 🔧 Configuração

Edite `config/settings.py` para personalizar:
- Tamanho da janela
- Cores do tema
- Configurações de log
- Parâmetros do sistema

## 🐛 Solução de Problemas

### Erro de Importação
- Verifique se o ambiente virtual está ativo
- Confirme se todas as dependências estão instaladas

### Erro de Banco de Dados
- Verifique permissões de escrita no diretório
- Confirme se o SQLite3 está funcionando

### Problemas de Interface
- Verifique a versão do Flet (deve ser 0.28.0)
- Confirme se o Python é 3.8+

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 👥 Autores

- Desenvolvido para o projeto Acesso2

## 📞 Suporte

Para suporte ou dúvidas, abra uma issue no repositório.

---

**Versão**: 1.0.0  
**Última atualização**: Dezembro 2024
