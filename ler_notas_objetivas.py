import os
import pdfplumber
import pandas as pd

from tqdm import tqdm
from checkhash import print_file_hash


def is_table_title(line: str) -> bool:
    for keyword in ["ACESSO DIRETO", "PRÉ-REQUISITO", "ANO ADICIONAL", "ÁREA DE ATUAÇÃO"]:
        if line.upper().startswith(keyword):
            return True
    return False


def is_valid(d):
    try:
        for i in range(2, 8):
            _ = int(d[i])
        return True
    except Exception:
        return False


def process_file(path: str):
    print_file_hash(os.getcwd(), path)
    print(f"Processando notas objetivas em {path}... Por favor aguarde.")

    data = []
    current_table_title = None

    with pdfplumber.open(path) as pdf:
        for page in tqdm(pdf.pages, desc="Lendo as páginas"):
            lines = page.extract_text().split("\n")
            for line in lines:
                if "ENARE 2024/2025 (Residência Médica)" in line:
                    continue  # Ignorar rodapés

                if is_table_title(line):
                    current_table_title = line.strip()  # Atualizar o título da tabela
                    continue

                if current_table_title and "Inscrição Nome" in line:
                    continue  # Ignora o cabeçalho

                if current_table_title and line.strip() and "ACESSO DIRETO" in current_table_title.upper():
                    # Separa os dados das linhas
                    parts = line.split()
                    if len(parts) >= 9:
                        inscricao = parts[0]
                        nome = " ".join(parts[1:-7])
                        cg = parts[-7]
                        cm = parts[-6]
                        prev = parts[-5]
                        go = parts[-4]
                        ped = parts[-3]
                        nota_obj = parts[-2]
                        sit = parts[-1]
                        data.append([inscricao, nome, cg, cm, prev, go, ped, nota_obj, sit, current_table_title])

    data = [d for d in tqdm(data, desc="Organizando os dados") if is_valid(d)]

    columns = [
        "Inscrição",
        "Nome",
        "Cirurgia Geral",
        "Clínica Médica",
        "Medicina Preventiva e Social",
        "Obstetrícia e Ginecologia",
        "Pediatria",
        "Nota Objetiva",
        "Situação",
        "Especialidade"
    ]

    df = pd.DataFrame(data, columns=columns)

    df["Cirurgia Geral"] = df["Cirurgia Geral"].astype(int)
    df["Clínica Médica"] = df["Clínica Médica"].astype(int)
    df["Medicina Preventiva e Social"] = df["Medicina Preventiva e Social"].astype(int)
    df["Obstetrícia e Ginecologia"] = df["Obstetrícia e Ginecologia"].astype(int)
    df["Pediatria"] = df["Pediatria"].astype(int)
    df["Nota Objetiva"] = df["Nota Objetiva"].astype(int)

    output_file = path.replace(".pdf", ".csv")
    df.to_csv(output_file, index=False)

    print(f"Dados extraídos no formato {df.shape} e salvos com sucesso em: {output_file}")
    print_file_hash(os.getcwd(), output_file)


if __name__ == '__main__':
    process_file("notas_objetivas.pdf")
