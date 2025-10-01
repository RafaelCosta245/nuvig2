import pdfplumber
import json
import re
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def escolher_arquivo():
    Tk().withdraw()  # Esconde a janela principal do tkinter
    arquivo = askopenfilename(title="Selecione o arquivo PDF", filetypes=[("Arquivos PDF", "*.pdf")])
    return arquivo

def parse_pdf(path):
    resultados = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            # --- Cabeçalho ---
            nome_match = re.search(r"Nome:\s*([^\n]+)", text)
            mesano_match = re.search(r"Mês/Ano:\s*([^\n]+)", text)
            matricula_match = re.search(r"Matrícula\s*([^\n]+)", text)

            nome = nome_match.group(1).strip() if nome_match else None
            mesano = mesano_match.group(1).strip() if mesano_match else None
            matricula = matricula_match.group(1).strip() if matricula_match else None

            # --- Tabela ---
            linhas = []
            table = page.extract_table()

            if table:
                headers = table[0]  # Cabeçalho da tabela: Dia da Semana, Dia, Registros dos Pontos, Horas Trabalhadas, Observação
                for row in table[1:]:
                    if len(row) >= 5:  # Verifica se a linha tem os 5 dados necessários
                        linha = {
                            "Dia da Semana": row[0],  # Ex: Seg1, Ter2
                            "Dia": row[1],            # Ex: 07/01, 08/02
                            "Registros": row[2],      # Ex: 07:52:34, 08:03:49
                            "Horas Trabalhadas": row[3],  # Ex: 38:33:32
                            "Observação": row[4] if len(row) > 4 else ""  # Observação se disponível
                        }
                        linhas.append(linha)

            # --- Resumo da página ---
            resultados.append({
                "Nome": nome,
                "MesAno": mesano,
                "Matricula": matricula,
                "Registros": linhas
            })

    return resultados

if __name__ == "__main__":
    caminho_pdf = escolher_arquivo()  # Chama a função para escolher o arquivo
    if caminho_pdf:
        dados = parse_pdf(caminho_pdf)

        # Imprime no console em formato JSON
        print(json.dumps(dados, indent=4, ensure_ascii=False))
    else:
        print("Nenhum arquivo foi selecionado.")
