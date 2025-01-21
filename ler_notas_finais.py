import os
import pdfplumber
import pandas as pd

from tqdm import tqdm

from checkhash import print_file_hash


def is_table_title(line):
    for keyword in ["ACESSO DIRETO", "PRÉ-REQUISITO", "ANO ADICIONAL", "ÁREA DE ATUAÇÃO"]:
        if line.upper().startswith(keyword):
            return True
    return False


def is_footer(line):
    return "ENARE 2024/2025 (Residência Médica)" in line


def process_file(path: str):
    print_file_hash(os.getcwd(), path)
    print(f"Processando notas do currículo em {path}... Por favor aguarde.")

    data = []
    current_table_title = None

    with pdfplumber.open(path) as pdf:
        for page in tqdm(pdf.pages, desc="Lendo as páginas"):
            lines = page.extract_text().split("\n")
            for line in lines:
                if is_footer(line):
                    continue  # Ignorar rodapés

                if is_table_title(line):
                    current_table_title = line.strip()  # Atualizar o título da tabela
                    continue

                if current_table_title and "NOME" in line and "ANÁLISE CURRICULAR" in line:
                    continue  # Ignora o cabeçalho

                if "Nota do Nota da" in line or line.strip() == "Nota" or "Inscrição" in line or line == "Final" or "Curricular" in line:
                    continue

                if " - Liminar" in line:
                    line = line.replace(" - Liminar", "-Liminar")

                if current_table_title and line.strip() and "ACESSO DIRETO" in current_table_title.upper():
                    # Separa os dados das linhas
                    parts = line.split()
                    if len(parts) >= 6:
                        nome = " ".join(parts[:-5])
                        inscricao = parts[-5]
                        nota_obj = parts[-4]
                        nota_curr = parts[-3]
                        bonif = parts[-2]
                        nota_f = parts[-1]
                        row = [nome, inscricao, nota_obj, nota_curr, bonif, nota_f, current_table_title]
                        data.append(row)

    columns = ["NOME", "INSCRIÇÃO", "OBJ", "CURR", "BONUS", "FINAL", "ESPECIALIDADE"]
    df = pd.DataFrame(data, columns=columns)

    for n in ["OBJ", "CURR", "FINAL"]:
        df[n] = df[n].str.replace(",", ".").astype(float)

    output_file = path.replace(".pdf", ".csv")
    df.to_csv(output_file, index=False)

    print(f"Dados extraídos no formato {df.shape} e salvos com sucesso em: {output_file}")
    print_file_hash(os.getcwd(), output_file)


if __name__ == '__main__':
    process_file("nota-final-enare-residencia-medica.pdf")
