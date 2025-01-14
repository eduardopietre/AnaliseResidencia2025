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

                if current_table_title and line.strip() and "ACESSO DIRETO" in current_table_title.upper():
                    # Separa os dados das linhas
                    parts = line.split()
                    if len(parts) >= 3:
                        nome = " ".join(parts[:-2])
                        inscricao = parts[-2]
                        nota = parts[-1]
                        row = [nome, inscricao, nota, current_table_title]
                        data.append(row)

    columns = ["NOME", "INSCRIÇÃO", "NOTA_DA_ANÁLISE_CURRICULAR", "ESPECIALIDADE"]
    df = pd.DataFrame(data, columns=columns)

    df["NOTA_DA_ANÁLISE_CURRICULAR"] = df["NOTA_DA_ANÁLISE_CURRICULAR"].str.replace(",", ".").astype(float)

    output_file = path.replace(".pdf", ".csv")
    df.to_csv(output_file, index=False)

    print(f"Dados extraídos no formato {df.shape} e salvos com sucesso em: {output_file}")
    print_file_hash(os.getcwd(), output_file)


if __name__ == '__main__':
    process_file("notas_curriculo.pdf")
